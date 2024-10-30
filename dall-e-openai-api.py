import tkinter as tk
from tkinter import filedialog, Canvas, Label
from PIL import Image, ImageTk
import requests
import io
import base64
from io import BytesIO

class ChatGPTImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatGPT Image Generator")
        self.root.geometry("1200x800")
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Load API token
        self.api_token = self.load_token("token.txt")
        
        # Chat Frame (Left)
        chat_frame = tk.Frame(root)
        chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Question area
        self.question_box = tk.Text(chat_frame, height=5, width=50)
        self.question_box.pack(fill="x", pady=10)
        self.question_box.insert(tk.END, "Type your question or image prompt here...")
        
        # Chat history
        self.chat_history = tk.Text(chat_frame, height=30)
        self.chat_history.pack(fill="both", expand=True)
        
        # Send button
        self.send_button = tk.Button(chat_frame, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)
        
        # Image Frame (Right)
        image_frame = tk.LabelFrame(root, text="Generated Image")
        image_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Image canvas
        self.image_canvas = tk.Canvas(image_frame, width=512, height=512)
        self.image_canvas.pack(fill="both", expand=True)
        
        # Generate Image button
        self.generate_button = tk.Button(image_frame, text="Generate Image", command=self.generate_image)
        self.generate_button.pack(pady=5)

    def load_token(self, filepath):
        try:
            with open(filepath, "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            print("Token file not found. Please add your token to token.txt")
            return None

    def send_message(self):
        if not self.api_token:
            self.chat_history.insert(tk.END, "Error: API token missing\n")
            return
            
        prompt = self.question_box.get("1.0", tk.END).strip()
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response_data = response.json()
            answer = response_data["choices"][0]["message"]["content"]
            
            self.chat_history.insert(tk.END, f"\nYou: {prompt}\n")
            self.chat_history.insert(tk.END, f"ChatGPT: {answer}\n")
            self.chat_history.see(tk.END)
            self.question_box.delete("1.0", tk.END)
            
        except Exception as e:
            self.chat_history.insert(tk.END, f"Error: {str(e)}\n")

    def generate_image(self):
        if not self.api_token:
            self.chat_history.insert(tk.END, "Error: API token missing\n")
            return
            
        prompt = self.question_box.get("1.0", tk.END).strip()
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024"
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=payload
            )
            
            image_url = response.json()["data"][0]["url"]
            image_response = requests.get(image_url)
            image = Image.open(BytesIO(image_response.content))
            
            # Resize while maintaining aspect ratio
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            image = image.resize((512, 512), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            self.image_canvas.delete("all")
            self.image_canvas.create_image(0, 0, anchor="nw", image=photo)
            self.image_canvas.image = photo
            
            self.chat_history.insert(tk.END, f"\nGenerated image for prompt: {prompt}\n")
            
        except Exception as e:
            self.chat_history.insert(tk.END, f"Image generation error: {str(e)}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatGPTImageApp(root)
    root.mainloop()