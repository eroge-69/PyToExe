# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: app.py
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import firebase_admin
from firebase_admin import credentials, auth, firestore
import requests
import asyncio
import random
from datetime import datetime, timedelta
import sys
import threading
from pyppeteer import connect
import sqlite3
import paypalrestsdk
import webbrowser
import re
import json
import base64
import subprocess
import uuid
from zoneinfo import ZoneInfo
singapore_tz = ZoneInfo('Asia/Singapore')
now_singapore = datetime.now(singapore_tz)
api_key = 'AIzaSyCqQMoSgx1mZrRLKJzewX1glN0owFKucWc'

def create_settings(self):
    settings_frame = tk.Frame(self.tab2, bg=self.bg_color)
    settings_frame.pack(fill=tk.X, pady=10, padx=5, anchor='w')
    tk.Label(settings_frame, text='Captcha Solver', fg=self.text_color, bg=self.bg_color, font=('Helvetica', 14)).pack(anchor='w')
    delay_frame = tk.Frame(settings_frame, bg=self.bg_color)
    delay_frame.pack(fill=tk.X, pady=5, anchor='w')
    tk.Label(delay_frame, text='Captcha Delay:', fg=self.text_color, bg=self.bg_color).pack(anchor='w')
    delay_min_frame = tk.Frame(delay_frame, bg=self.bg_color)
    delay_min_frame.pack(fill=tk.X, padx=5, anchor='w')
    tk.Label(delay_min_frame, text='Min', fg=self.text_color, bg=self.bg_color).pack(side='left')
    self.captcha_delay_min_entry = tk.Entry(delay_min_frame, textvariable=self.captcha_delay_min, bg=self.text_color, fg=self.bg_color, width=5)
    self.captcha_delay_min_entry.pack(side='left', padx=(5, 0))
    tk.Label(delay_min_frame, text='Max', fg=self.text_color, bg=self.bg_color).pack(side='left', padx=(10, 0))
    self.captcha_delay_max_entry = tk.Entry(delay_min_frame, textvariable=self.captcha_delay_max, bg=self.text_color, fg=self.bg_color, width=5)
    self.captcha_delay_max_entry.pack(side='left', padx=(5, 0))
    tk.Label(delay_min_frame, text='seconds', fg=self.text_color, bg=self.bg_color).pack(side='left', padx=(10, 0))
    steps_frame = tk.Frame(settings_frame, bg=self.bg_color)
    steps_frame.pack(fill=tk.X, pady=5, anchor='w')
    tk.Label(steps_frame, text='Mouse movement:', fg=self.text_color, bg=self.bg_color).pack(anchor='w')
    steps_min_frame = tk.Frame(steps_frame, bg=self.bg_color)
    steps_min_frame.pack(fill=tk.X, padx=5, anchor='w')
    tk.Label(steps_min_frame, text='Min', fg=self.text_color, bg=self.bg_color).pack(side='left')
    self.steps_min_entry = tk.Entry(steps_min_frame, textvariable=self.captcha_steps_min, bg=self.text_color, fg=self.bg_color, width=5)
    self.steps_min_entry.pack(side='left', padx=(5, 0))
    tk.Label(steps_min_frame, text='Max', fg=self.text_color, bg=self.bg_color).pack(side='left', padx=(10, 0))
    self.steps_max_entry = tk.Entry(steps_min_frame, textvariable=self.captcha_steps_max, bg=self.text_color, fg=self.bg_color, width=5)
    self.steps_max_entry.pack(side='left', padx=(5, 0))
    tk.Label(steps_min_frame, text='steps', fg=self.text_color, bg=self.bg_color).pack(side='left', padx=(10, 0))
    divider = tk.Frame(settings_frame, height=2, bd=1, relief='sunken', bg=self.text_color)
    divider.pack(fill=tk.X, pady=10)

    def on_closing(self):
        self.stop_captcha_task = True
        self.captcha_task_running = False
        for thread in threading.enumerate():
            if thread is not threading.current_thread():
                thread.join(timeout=1)
        self.root.quit()
        self.root.destroy()
        conn.close()
        os._exit(0)

    def toggle_captcha_task(self):
        if not self.captcha_task_running:
            self.captcha_task_running = True
            self.stop_captcha_task = False
            self.captcha_toggle_button.config(text='Stop Captcha Solver')
            self.start_captcha_task()
            return
        self.stop_captcha_task = True
        self.captcha_task_running = False
        self.captcha_toggle_button.config(text='Start Captcha Solver')
        asyncio.run(self.log_captcha('Captcha task stopped.'))

    def start_captcha_task(self):
        threading.Thread(target=lambda: asyncio.run(self.captcha_async_main())).start()

    async def captcha_async_main(self):
        if not self.current_user:
            await self.log_captcha('No authenticated user.')
            return
        else:  # inserted
            user_ref = db.collection('users').document(self.current_user['localId'])
            user_data = user_ref.get().to_dict()
            browser = None
            connected = False
            for attempt in range(1, max_retries + 1):
                try:
                    await self.log_captcha(f'Attempt {attempt}: Connecting to Tiktok Live Studio')
                except TimeoutError:
                        connect_task = asyncio.create_task(connect(browserURL='http://localhost:9222', defaultViewport=None))
                        timeout_task = asyncio.create_task(asyncio.sleep(connection_timeout / 1000))
                        done, pending = await asyncio.wait([connect_task, timeout_task], return_when=asyncio.FIRST_COMPLETED)
                if not connected:
                    await self.log_captcha('Failed to connect to the Tiktok Live Studio after several attempts.')
                    return
                else:  # inserted
                    await self.log_captcha('Fetching pages')
                    pages = await browser.pages()
                    if len(pages) < 1:
                        await self.log_captcha('Error: Could not find the expected page. Make sure the Tiktok Live Studio is running and debuggable.')
                        return
                    else:  # inserted
                        self = None
                        for current_page in pages:
                            title = await current_page.title()
                            if title == 'TikTok LIVE Studio':
                                await self.log_captcha('Identified the TikTok LIVE Studio page.')
                                element2 = await current_page.querySelector('.tt-live-toastV2-list-wrapper')
                                element3 = await current_page.querySelector('.index-module__title-wrapper--xoBmX')
                                if element2 or element3:
                                    self = current_page
                                    await self.log_captcha('Found the expected element on the page.')
                                    break
                        if not self:
                            await self.log_captcha('Error: Could not find the expected page with the specified title and element.')
                        else:  # inserted
                            await self.log_captcha('Successfully connected to the desired page.')
                            await self.scrape_and_update_tiktok_username(self)

                            async def check_for_captcha():
                                pass  # postinserted
                            while self.captcha_task_running:
                                if self.stop_captcha_task:
                                    await self.log_captcha('Captcha task is stopping.')
                                    return
                                else:  # inserted
                                    await check_for_captcha()
                await self.log_captcha(f'Attempt {attempt} failed: Connection timed out.')
                await self.log_captcha('Waiting for captcha to appear')
                captcha_popup = await page.xpath('//*[@id=\"captcha-mount-point\"]/div/div[2]')
                if captcha_popup:
                        for i in range(1, 31):
                            captcha_whirl = await page.xpath('//div[contains(text(), \'Drag the slider to fit the puzzle\')]')
                            captcha_threed = await page.xpath('//div[contains(text(), \'Select 2 objects that are the same shape:\')]')
                            captcha_icon = await page.xpath('//div[starts-with(text(), \'Which of these objects\')]')
                            captcha_puzzle = await page.xpath('//*[@id=\"captcha-mount-point\"]/div/div[2]')
                            if captcha_whirl:
                                whirl_captcha_location = await page.xpath('//div[contains(@class,\"secsdk-captcha-drag-icon\")]//*[name()=\"svg\"]')
                                if whirl_captcha_location:
                                    coordinate_whirl_captcha = await whirl_captcha_location[0].boundingBox()
                                    if coordinate_whirl_captcha is None:
                                        await self.log_captcha('Captcha Whirl Not Visible')
                                        return
                                    else:  # inserted
                                        await self.log_captcha('Captcha Whirl Is Visible')
                                        random_delay = random.randint(int(self.captcha_delay_min.get()), int(self.captcha_delay_max.get()))
                                        await self.log_captcha(f'Waiting for {random_delay} seconds to solve the captcha')
                                        await asyncio.sleep(random_delay)
                                        await self.log_captcha(f'Attempt {i}: Attempting to solve captcha whirl')
                                        coordinate_whirl_captcha_x = coordinate_whirl_captcha['x']
                                        coordinate_whirl_captcha_y = coordinate_whirl_captcha['y']
                                        await page.waitForXPath('//div[contains(@class,\"secsdk-captcha-drag-icon\")]//*[name()=\"svg\"]', {'visible': True, 'timeout': 30000})
                                        await page.waitForXPath('//img[@data-testid=\"whirl-outer-img\"]', {'visible': True, 'timeout': 30000})
                                        await page.waitForXPath('//img[@data-testid=\"whirl-inner-img\"]', {'visible': True, 'timeout': 30000})
                                        try:
                                            await page.waitForXPath('//img[@data-testid=\"whirl-outer-img\"]', {'visible': True, 'timeout': 30000})
                                        except Exception as error:
                                                await self.log_captcha('whirl outer image is visible on the page.')
                                        except Exception as error:
                                                await self.log_captcha('whirl inner image is visible on the page.')
                                        whirl_outer_image_src = await (await whirl_outer_image[0].getProperty('src')).jsonValue()
                                        await self.log_captcha('whirl outer image loaded')
                                        whirl_inner_image = await page.xpath('//img[@data-testid=\"whirl-inner-img\"]')
                                        whirl_inner_image_src = await (await whirl_inner_image[0].getProperty('src')).jsonValue()
                                        await self.log_captcha('whirl inner image loaded')
                                        url = 'https://tiktok-captcha-solver6.p.rapidapi.com/whirl'
                                        payload = {'b64External_or_url': whirl_outer_image_src, 'b64Internal_or_url': whirl_inner_image_src, 'width': '306', 'height': '40'}
                                        headers = {'x-rapidapi-key': '19b1c9774fmsh87a3566e350f2b2p11cc02jsn07337581c381', 'x-rapidapi-host': 'tiktok-captcha-solver6.p.rapidapi.com', 'Content-Type': 'application/json'}
                                        await self.log_captcha('Connecting to API')
                                        try:
                                            await self.log_captcha('Sending request to ChiliCaptcha API...')
                                        except Exception as error:
                                                response = requests.post(url, json=payload, headers=headers)
                                                response_data = response.json()
                                                await self.log_captcha('Request Sent')
                                else:  # inserted
                                    await self.log_captcha('Captcha Puzzle Not Visible')
                            else:  # inserted
                                if captcha_threed:
                                    threed_captcha_location = await page.xpath('//div[contains(@class,\"verify-captcha-submit-button\")]')
                                    if threed_captcha_location:
                                        coordinate_threed_captcha = await threed_captcha_location[0].boundingBox()
                                        if coordinate_threed_captcha is None:
                                            await self.log_captcha('Captcha 3D Not Visible')
                                            return
                                        else:  # inserted
                                            await self.log_captcha('Captcha 3D Is Visible')
                                            random_delay = random.randint(int(self.captcha_delay_min.get()), int(self.captcha_delay_max.get()))
                                            await self.log_captcha(f'Waiting for {random_delay} seconds to solve the captcha')
                                            await asyncio.sleep(random_delay)
                                            await self.log_captcha(f'Attempt {i}: Attempting to solve captcha 3D')
                                            coordinate_threed_captcha_x = coordinate_threed_captcha['x']
                                            coordinate_threed_captcha_y = coordinate_threed_captcha['y']
                                            await page.waitForXPath('//div[contains(@class,\"verify-captcha-submit-button\")]', {'visible': True, 'timeout': 30000})
                                            await page.waitForXPath('//img[@id=\"captcha-verify-image\"]', {'visible': True, 'timeout': 30000})
                                            try:
                                                await page.waitForXPath('//img[@id=\"captcha-verify-image\"]', {'visible': True, 'timeout': 30000})
                                            except Exception as error:
                                                    await self.log_captcha('3D Objects are not visible')
                                            threed_verify_image_src = await (await threed_verify_image[0].getProperty('src')).jsonValue()
                                            await self.log_captcha('3D Objects loaded')
                                            url = 'https://tiktok-captcha-solver6.p.rapidapi.com/3d'
                                            payload = {'b64External_or_url': threed_verify_image_src, 'width': '306', 'height': '191'}
                                            headers = {'x-rapidapi-key': '19b1c9774fmsh87a3566e350f2b2p11cc02jsn07337581c381', 'x-rapidapi-host': 'tiktok-captcha-solver6.p.rapidapi.com', 'Content-Type': 'application/json'}
                                            await self.log_captcha('Connecting to API')
                                            try:
                                                await self.log_captcha('Sending request to ChiliCaptcha API...')
                                            except Exception as error:
                                                    response = requests.post(url, json=payload, headers=headers)
                                                    response_data = response.json()
                                                    await self.log_captcha('Request Sent')
                                    else:  # inserted
                                        await self.log_captcha('Captcha 3D Not Visible')
                                else:  # inserted
                                    if captcha_icon:
                                        icon_captcha_location = await page.xpath('//div[contains(@class,\"verify-captcha-submit-button\")]')
                                        if icon_captcha_location:
                                            coordinate_icon_captcha = await icon_captcha_location[0].boundingBox()
                                            if coordinate_icon_captcha is None:
                                                await self.log_captcha('Captcha Icon Not Visible')
                                                return
                                            else:  # inserted
                                                await self.log_captcha('Captcha Icon Is Visible')
                                                random_delay = random.randint(int(self.captcha_delay_min.get()), int(self.captcha_delay_max.get()))
                                                await self.log_captcha(f'Waiting for {random_delay} seconds to solve the captcha')
                                                await asyncio.sleep(random_delay)
                                                await self.log_captcha(f'Attempt {i}: Attempting to solve captcha icon')
                                                coordinate_icon_captcha_x = coordinate_icon_captcha['x']
                                                coordinate_icon_captcha_y = coordinate_icon_captcha['y']
                                                await page.waitForXPath('//div[contains(@class,\"verify-captcha-submit-button\")]', {'visible': True, 'timeout': 30000})
                                                await page.waitForXPath('//img[@id=\"captcha-verify-image\"]', {'visible': True, 'timeout': 30000})
                                                await page.waitForXPath('//div[contains(@class,\"captcha_verify_bar\")]', {'visible': True, 'timeout': 30000})
                                                try:
                                                    await page.waitForXPath('//img[@id=\"captcha-verify-image\"]', {'visible': True, 'timeout': 30000})
                                                except Exception as error:
                                                        await self.log_captcha('Icons are not visible')
                                                icon_verify_image_src = await (await icon_verify_image[0].getProperty('src')).jsonValue()
                                                await self.log_captcha('Icons loaded')
                                                icon_question = await page.waitForXPath('//div[contains(@class,\"captcha_verify_bar--title\")]//div[contains(@class,\"VerifyBar___StyledDiv\")]', {'visible': True, 'timeout': 30000})
                                                icon_question_text = await page.evaluate('(el) => el.textContent', icon_question)
                                                await self.log_captcha('Question loaded')
                                                url = 'https://tiktok-captcha-solver6.p.rapidapi.com/icon'
                                                payload = {'b64External_or_url': icon_verify_image_src, 'question': icon_question_text, 'width': '306', 'height': '191'}
                                                headers = {'x-rapidapi-key': '19b1c9774fmsh87a3566e350f2b2p11cc02jsn07337581c381', 'x-rapidapi-host': 'tiktok-captcha-solver6.p.rapidapi.com', 'Content-Type': 'application/json'}
                                                await self.log_captcha('Connecting to API')
                                                try:
                                                    await self.log_captcha('Sending request to ChiliCaptcha API...')
                                                except Exception as error:
                                                        response = requests.post(url, json=payload, headers=headers)
                                                        response_data = response.json()
                                                        await self.log_captcha('Request Sent')
                                        else:  # inserted
                                            await self.log_captcha('Captcha 3D Not Visible')
                                            continue
                                    else:  # inserted
                                        if captcha_puzzle:
                                            puzzle_captcha_location = await page.xpath('//div[contains(@class,\"secsdk-captcha-drag-icon\")]//*[name()=\"svg\"]')
                                            if puzzle_captcha_location:
                                                coordinate_puzzle_captcha = await puzzle_captcha_location[0].boundingBox()
                                                if coordinate_puzzle_captcha is None:
                                                    await self.log_captcha('Captcha Puzzle Not Visible')
                                                    return
                                                else:  # inserted
                                                    await self.log_captcha('Captcha Puzzle is Visible')
                                                    random_delay = random.randint(int(self.captcha_delay_min.get()), int(self.captcha_delay_max.get()))
                                                    await self.log_captcha(f'Waiting for {random_delay} seconds to solve the captcha')
                                                    await asyncio.sleep(random_delay)
                                                    await self.log_captcha(f'Attempt {i}: Attempting to solve captcha puzzle')
                                                    coordinate_puzzle_captcha_x = coordinate_puzzle_captcha['x']
                                                    coordinate_puzzle_captcha_y = coordinate_puzzle_captcha['y']
                                                    await page.waitForXPath('//div[contains(@class,\"secsdk-captcha-drag-icon\")]//*[name()=\"svg\"]', {'visible': True, 'timeout': 30000})
                                                    await page.waitForXPath('//*[@id=\"captcha-verify-image\"]', {'visible': True, 'timeout': 30000})
                                                    await page.waitForXPath('//*[@id=\"captcha-mount-point\"]/div/div[2]/img[2]', {'visible': True, 'timeout': 30000})
                                                    try:
                                                        await page.waitForXPath('//*[@id=\"captcha-verify-image\"]', {'visible': True, 'timeout': 30000})
                                                    except Exception as error:
                                                            await self.log_captcha('PUZZLE IMAGE is visible on the page.')
                                                    except Exception as error:
                                                            await self.log_captcha('PIECE IMAGE is visible on the page.')
                                                    puzzle_image_src = await (await puzzle_image[0].getProperty('src')).jsonValue()
                                                    await self.log_captcha('Puzzle image loaded')
                                                    piece_image = await page.xpath('//*[@id=\"captcha-mount-point\"]/div/div[2]/img[2]')
                                                    piece_image_src = await (await piece_image[0].getProperty('src')).jsonValue()
                                                    await self.log_captcha('Piece image loaded')
                                                    url = 'https://tiktok-captcha-solver6.p.rapidapi.com/slide'
                                                    payload = {'b64External_or_url': puzzle_image_src, 'b64Internal_or_url': piece_image_src, 'width': '348', 'height': '40'}
                                                    headers = {'x-rapidapi-key': '19b1c9774fmsh87a3566e350f2b2p11cc02jsn07337581c381', 'x-rapidapi-host': 'tiktok-captcha-solver6.p.rapidapi.com', 'Content-Type': 'application/json'}
                                                    await self.log_captcha('Connecting to API')
                                                    try:
                                                        await self.log_captcha('Sending request to ChiliCaptcha API...')
                                                    except Exception as error:
                                                            response = requests.post(url, json=payload, headers=headers)
                                                            response_data = response.json()
                                                            await self.log_captcha('Request Sent')
                                            else:  # inserted
                                                await self.log_captcha('Captcha Puzzle Not Visible')
                        else:  # inserted
                          try:
                            await self.log_captcha('No captcha found')
                            await self.log_captcha('Timeout triggered, whirl outer image was not found within 30 seconds. Check your internet connection.')
                            await self.log_captcha('Timeout triggered, whirl inner image was not found within 30 seconds. Check your internet connection.')
                            await self.log_captcha(f'Error solving captcha: {error}')
                            await self.log_captcha('Timeout triggered, 3D Objects was not found within 30 seconds. Check your internet connection.')
                            await self.log_captcha(f'Error solving captcha: {error}')
                            await self.log_captcha('Timeout triggered, Icons was not found within 30 seconds. Check your internet connection.')
                            await self.log_captcha(f'Error solving captcha: {error}')
                            await self.log_captcha('Timeout triggered, PUZZLE IMAGE was not found within 30 seconds. Check your internet connection.')
                            await self.log_captcha('Timeout triggered, PIECE IMAGE was not found within 30 seconds. Check your internet connection.')
                            await self.log_captcha(f'Error solving captcha: {error}')
                          except Exception as error:
                             await self.log_captcha(f'Attempt {attempt} failed: {error}')
                if attempt < max_retries:
                    await asyncio.sleep(retry_interval / 1000)

    def update_last_solved_label(self):
        current_time = now_singapore.strftime('%Y-%m-%d %H:%M:%S')
        self.last_solved_label.config(text=f'Last Captcha Solved: {current_time}')

def run():
    root = tk.Tk()
    app = CombinedApp(root)
    root.mainloop()
if __name__ == '__main__':
    run()