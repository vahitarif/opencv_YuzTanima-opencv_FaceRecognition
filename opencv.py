import cv2
import face_recognition
import ctypes
import tkinter as tk
from tkinter import ttk
import PIL.Image
import PIL.ImageTk

reference_image = face_recognition.load_image_file("referans.png")
reference_encoding = face_recognition.face_encodings(reference_image)[0]

video_capture = cv2.VideoCapture(0)

def lock_screen():
    ctypes.windll.user32.LockWorkStation()

similarity_percentages = []
max_similarity_count = 20

def check_face():
    similarity_percentage = None

    ret, frame = video_capture.read()

    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    if len(face_locations) == 0:
        log_similarity("Yüz algılanamadı.")
        log_similarity(str(face_locations))


    if len(face_encodings) == 0:
        log_similarity("Yüz bulunamadı.")
    
    for face_location, face_encoding in zip(face_locations, face_encodings):
        top, right, bottom, left = face_location
        similarity_percentage = face_recognition.face_distance([reference_encoding], face_encoding)[0]
        similarity_percentage = round((1 - similarity_percentage) * 100, 2)

        if similarity_percentage <= 45:
            print("Yüz tanıma başarısız.")
            lock_screen()

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        text_color = (0, 255, 0)
        cv2.putText(frame, f'similarity: {similarity_percentage}%', (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, text_color, 2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        root.quit()

    img = PIL.Image.fromarray(frame)
    img = img.resize((400, 300))
    imgtk = PIL.ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)
    video_label.after(1, check_face)

    update_similarity_log(similarity_percentage)

def update_similarity_log(similarity_percentage):
    if similarity_percentage is not None:
        similarity_percentages.append(similarity_percentage)
        if len(similarity_percentages) > max_similarity_count:
            similarity_percentages.pop(0)
    log_text = ([f'similarity: {sp}%' for sp in similarity_percentages])
    log_window.config(state="normal")
    log_window.delete("1.0", tk.END)
    log_window.insert(tk.END, log_text)
    
    log_window.tag_configure("red", foreground="red")
    log_window.tag_configure("green", foreground="green")
    for sp in similarity_percentages:
        if sp <= 55:
            log_window.insert(tk.END,"\n" f'similarity: {sp}%', "red")
            log_window.insert(tk.END, "\n")  
        else:
            log_window.insert(tk.END,"\n" f'similarity: {sp}%', "green")
        log_window.insert(tk.END, "\n")
    
    log_window.config(state="disabled", bg="black")

def log_similarity(message):
    log_window.config(state="normal")
    log_window.insert(tk.END, "\n"f"{message}\n", "red")
    log_window.config(state="disabled", bg="black")

def clear_similarity_log():
    similarity_percentages.clear()
    log_window.config(state="normal")
    log_window.delete("1.0", tk.END)
    log_window.config(state="disabled", bg="black")


root = tk.Tk()
root.title("Face Recognition")


main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True)

log_window = tk.Text(main_frame, font=("Helvetica", 12), state="disabled", bg="black")
log_window.pack(side="right", padx=10, pady=10, fill="both", expand=True)

video_label = tk.Label(main_frame)
video_label.pack(side="top", anchor="ne")

controls_frame = ttk.Frame(main_frame)
controls_frame.pack(side="left", padx=10, pady=10)

clear_button = ttk.Button(main_frame, text="Clear Log", command=clear_similarity_log)
clear_button.pack(side="right", padx=10, pady=10)

check_face()

root.mainloop()

video_capture.release()
cv2.destroyAllWindows()
