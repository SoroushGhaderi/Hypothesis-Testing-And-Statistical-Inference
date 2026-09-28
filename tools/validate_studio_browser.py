#!/usr/bin/env python3
"""Browser regression checks for Learning Studio themes; requires Playwright Chromium.

Run: python tools/validate_studio_browser.py --output /tmp/studio-validation
The optional output directory receives screenshots and a JSON evidence summary.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
THEME_KEY = 'hypothesis_testing_course_theme_v1'
LANGUAGE_KEY = 'hypothesis_testing_course_language_v1'
ILLUSTRATIONS = {f"lesson_{spec['lesson']:02d}": spec for spec in json.loads((ROOT / 'tools/course_illustrations.json').read_text())}

# Inspect rendered text across the entire active page, including below the fold.
# This targets solid backgrounds used by this site; it is not a complete WCAG audit.
CONTRAST_AUDIT = r"""() => {
  const rgb = value => (value.match(/[\d.]+/g) || []).map(Number);
  const blend = (fg, bg) => {
    const alpha = fg.length > 3 ? fg[3] : 1;
    return fg.slice(0, 3).map((v, i) => v * alpha + bg[i] * (1 - alpha));
  };
  const background = el => {
    const stack = []; for (let node = el; node; node = node.parentElement) stack.unshift(node);
    return stack.reduce((bg, node) => blend(rgb(getComputedStyle(node).backgroundColor), bg), [255,255,255]);
  };
  const luminance = color => color.map(v => {
    v /= 255; return v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4;
  }).reduce((sum, v, i) => sum + v * [.2126,.7152,.0722][i], 0);
  const ratio = (a,b) => { const x=luminance(a), y=luminance(b); return (Math.max(x,y)+.05)/(Math.min(x,y)+.05); };
  const failures = []; let checked=0, minimum=Infinity;
  const inspect = (el, text, color) => {
    const style = getComputedStyle(el), bg=background(el), value=ratio(blend(rgb(color || style.color),bg),bg);
    const large = parseFloat(style.fontSize) >= 24 || (parseFloat(style.fontSize) >= 18.6667 && parseInt(style.fontWeight) >= 700);
    checked++; minimum=Math.min(minimum,value);
    if (value < (large ? 3 : 4.5)) failures.push({selector:el.tagName+'.'+el.className,text:text.slice(0,100),ratio:+value.toFixed(3),color:style.color,bg});
  };
  for (const el of document.querySelectorAll('body *')) {
    if (el.closest('script,style,annotation,select,option') || !el.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})) continue;
    if (innerWidth <= 760 && el.closest('.course_sidebar') && !document.body.classList.contains('nav_open')) continue;
    const text = [...el.childNodes].filter(n=>n.nodeType===Node.TEXT_NODE).map(n=>n.textContent).join('').trim();
    if (text) inspect(el,text);
  }
  for (const el of document.querySelectorAll('input[type=search],select')) {
    if (!el.checkVisibility() || (innerWidth <= 760 && el.closest('.course_sidebar') && !document.body.classList.contains('nav_open'))) continue;
    inspect(el,el.value || el.placeholder,el.placeholder && !el.value ? getComputedStyle(el,'::placeholder').color : null);
  }
  return {checked,minimum:+minimum.toFixed(3),failures};
}"""


def run(output: Path | None) -> dict:
    summary = {'url': (ROOT / 'course.html').as_uri(), 'page_checks': [], 'illustration_checks': [], 'interaction_checks': [], 'errors': []}
    if output:
        output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={'width':1440,'height':1000},color_scheme='light')
        page = context.new_page()
        page.on('pageerror', lambda error: summary['errors'].append(str(error)))
        page.goto(summary['url'])
        ids = page.locator('.course_page').evaluate_all('(pages)=>pages.map(p=>p.id)')
        assert len(ids) == 20
        for width in [1440, 768, 390, 320]:
            page.set_viewport_size({'width':width,'height':1000 if width > 760 else 844})
            for language in ['en','fa']:
                page.locator('#language_select').select_option(language)
                for theme in ['light','dark']:
                    if page.locator('html').get_attribute('data-theme') != theme:
                        page.locator('#theme_button').click()
                    for identifier in ids:
                        page.evaluate('(id)=>location.hash=id',identifier)
                        page.wait_for_function('(id)=>document.querySelector(".course_page.active").id===id',arg=identifier)
                        if language == 'fa':
                            page.wait_for_function('document.documentElement.lang === "fa"')
                            # showPage schedules localization on the next task.
                            page.evaluate('()=>new Promise(resolve=>setTimeout(resolve,0))')
                        if identifier in ILLUSTRATIONS:
                            spec = ILLUSTRATIONS[identifier]
                            figure = page.locator(f'#{identifier} .lesson_illustration')
                            assert figure.count() == 1
                            image = figure.locator('img')
                            image.scroll_into_view_if_needed()
                            page.wait_for_function('(id)=>{const img=document.querySelector(`#${id} .lesson_illustration img`);return img.complete && img.naturalWidth>0}',arg=identifier)
                            assert image.get_attribute('src') == spec['src']
                            assert image.evaluate('(img)=>[img.naturalWidth,img.naturalHeight]') == [spec['width'],spec['height']]
                            suffix = '_fa' if language == 'fa' else ''
                            assert image.get_attribute('alt') == spec['alt'+suffix]
                            assert figure.locator('figcaption p').first.inner_text() == spec['caption'+suffix]
                            assert figure.locator('.illustration_labels').inner_text() == spec['labels_text'+suffix]
                            assert figure.locator('.illustration_open').get_attribute('href') == spec['src']
                            summary['illustration_checks'].append({'page':identifier,'width':width,'language':language,'theme':theme,'loaded':True})
                        audit = page.evaluate(CONTRAST_AUDIT)
                        assert not audit['failures'], (width,language,theme,identifier,audit['failures'][:5])
                        overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
                        assert not overflow, ('horizontal overflow',width,language,theme,identifier)
                        summary['page_checks'].append({'width':width,'language':language,'theme':theme,'page':identifier,'text_nodes':audit['checked'],'minimum_contrast':audit['minimum']})
                    if output and width in [1440,390] and language == 'en':
                        for identifier in ['course_overview','lesson_03','lesson_08','lesson_13']:
                            page.evaluate('(id)=>location.hash=id',identifier)
                            page.wait_for_function('(id)=>document.querySelector(".course_page.active").id===id',arg=identifier)
                            page.screenshot(path=str(output/f'{identifier}-{width}-{theme}.png'),full_page=True)
        # Test hover, focus, checked progress, menu, search empty/filtered, and theme localization.
        page.set_viewport_size({'width':390,'height':844})
        for theme in ['light','dark']:
            if page.locator('html').get_attribute('data-theme') != theme:
                page.locator('#theme_button').click()
            page.locator('#language_select').select_option('en')
            page.locator('#menu_button').click()
            assert page.locator('body').evaluate('(el)=>el.classList.contains("nav_open")')
            page.locator('#course_search').fill('Welch topic that is absent')
            assert page.locator('#empty_search').is_visible()
            page.locator('#course_search').fill('paired')
            assert page.locator('.nav_link:not(.hidden)').count() >= 1
            page.locator('#course_search').fill('')
            page.locator('.nav_link[data-page="lesson_03"]').click()
            page.wait_for_function('document.querySelector(".course_page.active").id === "lesson_03"')
            assert not page.locator('body').evaluate('(el)=>el.classList.contains("nav_open")')
            check = page.locator('#lesson_03 [data-progress]')
            check.check()
            assert '1 of 15' in page.locator('#progress_text').inner_text()
            check.uncheck()
            for selector in ['#theme_button','#lesson_03 .lesson_complete','#lesson_03 .page_nav a']:
                page.locator(selector).first.hover()
                assert not page.evaluate(CONTRAST_AUDIT)['failures']
                page.locator(selector).first.focus()
            page.locator('#language_select').focus()
            page.keyboard.press('Tab')
            assert page.locator('#theme_button').evaluate('(el)=>el.matches(":focus-visible")')
            page.keyboard.press('Space')
            changed = 'dark' if theme=='light' else 'light'
            assert page.locator('html').get_attribute('data-theme') == changed
            assert page.locator('#theme_button').get_attribute('aria-pressed') == str(changed=='dark').lower()
            page.reload()
            assert page.locator('html').get_attribute('data-theme') == changed
            # Theme must survive a language change; labels must not restore the old contrast toggle.
            page.locator('#language_select').select_option('fa')
            assert page.locator('#theme_button').get_attribute('aria-label') == 'حالت شب'
            assert page.locator('html').get_attribute('data-theme') == changed
            page.locator('#language_select').select_option('en')
            assert page.locator('#theme_button').get_attribute('aria-label') == 'Night mode'
            summary['interaction_checks'].append(f'{theme}: menu/search/progress/hover/focus/keyboard/reload/language')
        # Follow the system until an explicit choice exists; stored preference wins afterwards.
        page.evaluate('(key)=>localStorage.removeItem(key)',THEME_KEY)
        page.emulate_media(color_scheme='dark')
        page.reload()
        assert page.locator('html').get_attribute('data-theme') == 'dark'
        page.emulate_media(color_scheme='light')
        page.wait_for_function('document.documentElement.dataset.theme === "light"')
        page.locator('#theme_button').click()
        page.emulate_media(color_scheme='dark')
        page.emulate_media(color_scheme='light')
        assert page.locator('html').get_attribute('data-theme') == 'dark'
        page.reload()
        assert page.locator('html').get_attribute('data-theme') == 'dark'
        summary['interaction_checks'].append('system default/live change and explicit preference precedence')
        page.emulate_media(media='print')
        assert page.locator('html').evaluate('(el)=>getComputedStyle(el).colorScheme') == 'light'
        assert page.locator('body').evaluate('(el)=>getComputedStyle(el).backgroundColor') == 'rgb(255, 255, 255)'
        assert page.locator('#lesson_03 .module:not(.visual_lesson)').first.evaluate('(el)=>getComputedStyle(el).backgroundColor') == 'rgb(255, 255, 255)'
        summary['interaction_checks'].append('print uses light colors even with saved night mode')
        context.close()
        # Invalid and blocked storage must not break reading or toggling.
        for storage in ['invalid','blocked']:
            context = browser.new_context(color_scheme='dark')
            if storage == 'blocked':
                context.add_init_script("Object.defineProperty(window, 'localStorage', {get(){throw new Error('Storage blocked')}})")
            else:
                context.add_init_script(f"localStorage.setItem('{THEME_KEY}','unexpected')")
            tab=context.new_page()
            tab.on('pageerror',lambda error: summary['errors'].append(str(error)))
            tab.goto(summary['url'])
            assert tab.locator('html').get_attribute('data-theme') == 'dark'
            tab.locator('#theme_button').click()
            assert tab.locator('html').get_attribute('data-theme') == 'light'
            context.close()
            summary['interaction_checks'].append(f'{storage} storage: reading and toggle remain functional')
        browser.close()
    assert not summary['errors'], summary['errors']
    summary['total_page_checks']=len(summary['page_checks'])
    if output:
        (output/'validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    return summary


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='Save screenshots and validation.json')
    args=parser.parse_args()
    result=run(args.output)
    print(f"Passed {result['total_page_checks']} page/theme/language/viewport checks, {len(result['illustration_checks'])} illustration checks, {len(result['interaction_checks'])} interaction groups, and no JavaScript errors.")
