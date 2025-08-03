## Offlinemind

# Imports
import time
import requests
import pyperclip
import pyautogui
import pyttsx3
import tkinter as tk
from pynput import keyboard
from threading import Thread

# Global Variables
HOTKEY = keyboard.Key.f9
OLLAMA_API_URL = "http://localhost:3000/api/generate" # Ollama API endpoint (run using command 'OLLAMA_HOST=127.0.0.1:3000 ollama serve')
OLLAMA_MODEL = "gemma3n" # Model name
root = None

# Store the last selected text to avoid re-fetching on language change
last_selected_text = ""
last_mouse_x = -1
last_mouse_y = -1
response_window = None
response_label = None
language_var = None

# List of languages for the dropdown menu (added just few for demo but can be extended further)
available_languages = ["English", "Spanish", "French", "German", "Hindi", "Mandarin", "Japanese"]

# Initialize the root window
def init_root_window():
    """Initializes a hidden Tkinter root window."""
    global root
    if root is None:
        root = tk.Tk()
        root.withdraw()
        root.title("Offlinemind")

# Get the user selected text from the clipboard
def get_selected_text():
    """
    Simulates a copy command to get the currently selected text.
    Returns the text from the clipboard.
    """
    pyautogui.hotkey('command', 'c')
    time.sleep(0.1)
    return pyperclip.paste()

# Additional Feature: Speak the text selected by the user (added to help user understand the pronounciation of the text)
def speak_text(text):
    """
    Initializes a text-to-speech engine and speaks the given text.
    This runs on a separate thread to avoid blocking the main script.
    """
    try:
        tts_engine = pyttsx3.init()
        tts_engine.setProperty('rate', 180)
    except ImportError:
        print("pyttsx3 not installed. Text-to-speech will be disabled.")
        return

    def run_speech():
        tts_engine.say(text)
        tts_engine.runAndWait()
    
    speech_thread = Thread(target=run_speech)
    speech_thread.start()

# Function to get response from Gemma 3n model via Ollama API
def get_ollama_response(prompt):
    """
    Sends a prompt to the local Ollama server and returns the
    generated response text.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data['response']
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {e}. Please ensure Ollama is running and the '{OLLAMA_MODEL}' model is available."

# Worker function to to provide instruction prompt and handle UI updates
def ollama_worker(text_to_explain, language="English", is_initial_request=True):
    """
    Worker function to fetch the Ollama response in a separate thread.
    Schedules the UI update on the main thread after completion.
    """
    global last_mouse_x, last_mouse_y
    
    # Create the prompt with the new instructions
    prompt = f"Provide a short and concise explanation for the following text in {language}. If it is a word, provide a good definition and an example sentence for its daily use. If it is a sentence or a phrase, provide a clear and simple explanation without complex words. Do not write an essay or big paragraphs, just the explanation. The text to explain is: '{text_to_explain}'"
    
    # Update the UI with a "Thinking..." message
    if is_initial_request:
        root.after(0, show_response_window, "Thinking...", last_mouse_x, last_mouse_y)
    else:
        root.after(0, show_response_window, "Thinking...", -1, -1)
    
    response_text = get_ollama_response(prompt)
    print(f"Offlinemind response: '{response_text}'")

    # Update the UI with the final response
    if is_initial_request:
        root.after(0, show_response_window, response_text, last_mouse_x, last_mouse_y, language)
    else:
        root.after(0, show_response_window, response_text, -1, -1, language)

# Callback function for language change in the dropdown menu
def on_language_change(*args):
    """
    Callback function when the dropdown menu selection changes.
    Triggers a new Ollama request with the updated language.
    """
    global last_selected_text, last_mouse_x, last_mouse_y
    if last_selected_text:
        selected_language = language_var.get()
        print(f"Language changed to: {selected_language}. Re-requesting explanation.")
        # Start a new worker thread for the new language. is_initial_request is False
        ollama_thread = Thread(target=ollama_worker, args=(last_selected_text, selected_language, False))
        ollama_thread.start()

# Function to show the response window with the generated text and language dropdown
def show_response_window(text, x, y, selected_lang="English"):
    """
    Creates and displays a floating, transparent window with the
    generated text and a language dropdown.
    """
    global root, response_window, response_label, language_var
    
    if root is None:
        init_root_window()

    # Destroy any existing window before creating a new one
    if response_window and response_window.winfo_exists():
        response_window.destroy()

    response_window = tk.Toplevel(root)
    response_window.overrideredirect(True)
    response_window.attributes("-topmost", True)
    response_window.attributes("-alpha", 0.9)
    if x != -1 and y != -1:
        response_window.geometry(f"+{x-10}+{y-10}")
    else:
        # Center the window if coordinates are not provided (e.g., on language change)
        response_window.update_idletasks()
        window_width = response_window.winfo_width()
        window_height = response_window.winfo_height()
        screen_width = response_window.winfo_screenwidth()
        screen_height = response_window.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        response_window.geometry(f"+{center_x}+{center_y}")

    # Use a modern color palette
    frame = tk.Frame(response_window, bg="#2c2c2c", padx=15, pady=15, relief="flat", bd=0)
    frame.pack(fill="both", expand=True)

    # Dropdown menu for languages
    language_var = tk.StringVar(root)
    language_var.set(selected_lang)
    language_menu = tk.OptionMenu(frame, language_var, *available_languages)
    language_menu.config(
        bg="#444444",
        fg="#e0e0e0",
        font=("Helvetica", 11, "bold"),
        activebackground="#555555",
        activeforeground="#ffffff",
        highlightthickness=0
    )
    language_menu.pack(pady=(0, 5))
    language_var.trace("w", on_language_change)

    response_label = tk.Label(
        frame,
        text=text,
        bg="#010101",
        fg="#e0e0e0",
        font=("Helvetica", 13),
        wraplength=450,
        justify="left",
        pady=10
    )
    response_label.pack(fill="both", expand=True)

    def close_window_on_click(event=None):
        response_window.destroy()

    response_label.bind("<Button-1>", close_window_on_click)
    response_window.bind("<Button-1>", close_window_on_click)

    response_window.after(30000, response_window.destroy)

    response_window.deiconify()
    response_window.lift()
    response_window.focus_force()

# Listen for the hotkey press (F9) to trigger the Offlinemind
def on_hotkey_press():
    """
    This function is executed when the hotkey is pressed.
    It orchestrates the entire workflow.
    """
    global last_selected_text, last_mouse_x, last_mouse_y
    print("Hotkey pressed! Starting Offlinemind...")
    
    selected_text = get_selected_text().strip()
    if not selected_text:
        print("No text selected.")
        return
        
    print(f"Selected text: '{selected_text}'")
    last_selected_text = selected_text

    speak_text(selected_text)
    
    last_mouse_x, last_mouse_y = pyautogui.position()
    
    # Start the ollama_worker in a new thread.
    ollama_thread = Thread(target=ollama_worker, args=(selected_text,))
    ollama_thread.start()

# Function to handle key press events
def on_press(key):
    """
    The function called by pynput on any key press.
    """
    try:
        if key == HOTKEY:
            on_hotkey_press()
    except Exception as e:
        print(f"An error occurred: {e}")

# Main function to initialize the listener and root window
if __name__ == '__main__':
    print("Listening for F9 key press...")
    print("Make sure Ollama is running in your terminal with the Gemma 3n model available.")

    init_root_window()
    
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    root.mainloop()