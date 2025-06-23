import asyncio
from playwright.async_api import async_playwright
import gc
import weakref

# تحسينات للذاكرة والأداء
_page_cache = weakref.WeakSet()
_selector_cache = 'div.vwM69.OXbMa div.QPKNz span.nonIntl:has-text("انقر للمشاهدة")'

async def click_view_element(page):
    try:
        # استخدام query_selector بدلاً من wait_for_selector لتوفير الوقت
        view_element = await page.query_selector(_selector_cache)
        if view_element and await view_element.is_visible():
            await view_element.click(force=True, no_wait_after=True)
            return True
        
        # محاولة بديلة سريعة
        alt_elements = await page.query_selector_all('span:has-text("انقر للمشاهدة")')
        for element in alt_elements:
            if await element.is_visible():
                await element.click(force=True, no_wait_after=True)
                return True
                
    except:
        pass
    return False

async def handle_all_pages(context):
    while True:
        # تحسين جمع الصفحات النشطة
        active_pages = []
        for p in context.pages:
            if not p.is_closed() and p.url != "about:blank":
                active_pages.append(p)
                _page_cache.add(p)
        
        # تشغيل متوازي محسن
        if active_pages:
            tasks = [click_view_element(p) for p in active_pages]
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # تنظيف دوري للذاكرة
        if len(_page_cache) % 50 == 0:
            gc.collect()

async def main():
    async with async_playwright() as p:
        # نفس إعدادات المتصفح من بوت سناب الأساسي مع تحسينات إضافية
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--incognito",
                "--disable-blink-features=AutomationControlled",
                "--enable-parallel-downloading",
                "--enable-tcp-fast-open",
                "--disable-images",
                "--disable-plugins",
                "--disable-extensions",
                "--disable-background-networking",
                "--disable-notifications",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                "--disable-breakpad",
                "--disable-component-extensions-with-background-pages",
                "--disable-domain-reliability",
                "--no-service-autorun",
                "--disable-ipc-flooding-protection",
                "--disable-hang-monitor",
                "--disable-prompt-on-repost",
                # تحسينات إضافية للأداء
                "--enable-features=VizDisplayCompositor",
                "--disable-dev-shm-usage",
                "--disable-gpu-sandbox",
                "--disable-software-rasterizer",
                "--disable-background-media-suspend",
                "--disable-client-side-phishing-detection",
                "--disable-sync",
                "--disable-translate",
                "--hide-scrollbars",
                "--mute-audio",
                "--no-first-run",
                "--disable-default-apps",
                "--disable-popup-blocking",
                "--disable-zero-browsers-open-for-tests",
                "--use-gl=swiftshader",
                "--enable-webgl",
                "--ignore-gpu-blacklist",
                "--enable-accelerated-2d-canvas",
                "--num-raster-threads=4",
                "--enable-zero-copy"
            ],
            chromium_sandbox=False
        )

        # تحسينات السياق
        context = await browser.new_context(
            no_viewport=True,
            viewport={"width": 800, "height": 600},
            java_script_enabled=True,
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # تحسينات إضافية
            accept_downloads=False,
            bypass_csp=True,
            color_scheme='light',
            reduced_motion='reduce',
            forced_colors='none'
        )

        page = await context.new_page()
        
        # حظر المزيد من الموارد لتوفير الباندويث
        await page.route("**/*.{png,jpg,jpeg,webp,gif,svg,mp4,webm,avi,mov,woff,woff2,ttf,eot,otf,css,ico,pdf,zip,rar,exe,dmg,app,deb,rpm,msi,pkg,bin}", 
                       lambda route: route.abort())
        
        # حظر الطلبات التحليلية والإعلانية
        await page.route("**/analytics/**", lambda route: route.abort())
        await page.route("**/ads/**", lambda route: route.abort())
        await page.route("**/tracking/**", lambda route: route.abort())
        await page.route("**/metrics/**", lambda route: route.abort())
        await page.route("**/*google-analytics*", lambda route: route.abort())
        await page.route("**/*googletagmanager*", lambda route: route.abort())
        await page.route("**/*facebook.com*", lambda route: route.abort())
        await page.route("**/*doubleclick*", lambda route: route.abort())
        
        # تسريع التنقل
        await page.goto("https://www.snapchat.com/web/70cf7311-6471-4307-8637-d899f57afd19",
                      wait_until='commit', timeout=30000)

        # تحسين معالجة الصفحة
        await page.evaluate("""
            // تعطيل الرسوم المتحركة لتوفير الأداء
            document.documentElement.style.setProperty('--animation-duration', '0s', 'important');
            document.documentElement.style.setProperty('--animation-delay', '0s', 'important');
            document.documentElement.style.setProperty('--transition-duration', '0s', 'important');
            
            // تحسين التمرير
            document.documentElement.style.scrollBehavior = 'auto';
            
            // تعطيل التركيز التلقائي
            document.addEventListener('focus', e => e.preventDefault(), true);
        """)

        monitor_task = asyncio.create_task(handle_all_pages(context))
        
        try:
            while True:
                await asyncio.sleep(0)  # بدون أي وقت انتظار
        except:
            pass
        finally:
            monitor_task.cancel()
            # تنظيف سريع
            try:
                await context.close()
            except:
                pass
            try:
                await browser.close()
            except:
                pass

if __name__ == "__main__":
    # تحسين حلقة الأحداث
    try:
        if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except:
        pass
    
    asyncio.run(main())