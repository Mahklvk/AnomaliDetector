from flask import Flask, render_template, Response, jsonify
import cv2
import os
import random
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

class MediaApp:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.media_folder = "static/media_files"
        
        # Buat folder jika belum ada
        os.makedirs(self.media_folder, exist_ok=True)
        os.makedirs("templates", exist_ok=True)
        
        # Format file yang didukung
        self.image_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
        self.video_formats = ('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.webm')
    
    def generate_frames(self):
        """Generate webcam frames untuk streaming"""
        while True:
            success, frame = self.camera.read()
            if not success:
                break
            else:
                # Flip frame horizontally untuk mirror effect
                frame = cv2.flip(frame, 1)
                
                # Encode frame ke JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                
                # Yield frame untuk streaming
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    def get_random_media(self):
        """Ambil file media random"""
        media_files = []
        
        if os.path.exists(self.media_folder):
            for file in os.listdir(self.media_folder):
                if file.lower().endswith(self.image_formats + self.video_formats):
                    media_files.append(file)
        
        if not media_files:
            return None, None, None
        
        random_file = random.choice(media_files)
        
        if random_file.lower().endswith(self.image_formats):
            return random_file, 'image', f"/static/media_files/{random_file}"
        elif random_file.lower().endswith(self.video_formats):
            return random_file, 'video', f"/static/media_files/{random_file}"
        
        return None, None, None

# Inisialisasi aplikasi
media_app = MediaApp()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(media_app.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/random-media')
def random_media():
    filename, media_type, url = media_app.get_random_media()
    
    if filename:
        return jsonify({
            'success': True,
            'type': media_type,
            'url': url,
            'message': f'Inilah Anomali Kamu!!!'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Tidak ada file media ditemukan. Tambahkan file gambar/video ke folder static/media_files/'
        })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'File tidak ditemukan'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Terjadi kesalahan server'}), 500

if __name__ == '__main__':
    print("🚀 Starting Anomali Detector App...")
    print("📂 Pastikan folder 'static/media_files/' berisi file gambar/video")
    print("🌐 Buka browser dan akses: http://localhost:5000")
    print("💀 Klik tombol untuk menampilkan anomali random!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)