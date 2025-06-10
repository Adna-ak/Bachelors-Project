import json
import os
import random
import glob
import tkinter as tk
from PIL import Image, ImageTk
from twisted.internet.defer import inlineCallbacks, Deferred


class PrePostTestUI:
    def __init__(self, master, images_folder):
        self.master = master
        self.images_folder = images_folder
        self.selected_image = None
        self.image_buttons = []
        self.timeout_deferred = Deferred()

        self.frame = tk.Frame(master)
        self.frame.pack()

        self.images_frame = tk.Frame(self.frame)
        self.images_frame.pack()

    def show_images_with_timeout(self, images, word, timeout_secs=7):
        # Clear old buttons
        for btn in self.image_buttons:
            btn.destroy()
        self.image_buttons = []
        self.selected_image = None

        def on_click(image_file):
            if not self.timeout_deferred.called:
                self.selected_image = image_file
                self.timeout_deferred.callback(image_file)
                self.master.quit()

        # Display buttons in grid
        max_cols = 2
        for idx, img_file in enumerate(images):
            for folder in ["words", "fillers"]:
                path = os.path.join(self.images_folder, folder, img_file)
                if os.path.exists(path):
                    pil_img = Image.open(path).resize((300, 300))
                    tk_img = ImageTk.PhotoImage(pil_img)
                    btn = tk.Button(self.images_frame, image=tk_img,
                                    command=lambda f=img_file: on_click(f))
                    btn.image = tk_img
                    row = idx // max_cols
                    col = idx % max_cols
                    btn.grid(row=row, column=col, padx=20, pady=20)
                    self.image_buttons.append(btn)
                    break

        self.master.after(timeout_secs * 1000, self._on_timeout)
        self.master.mainloop()

        return self.timeout_deferred

    def _on_timeout(self):
        if not self.timeout_deferred.called:
            self.timeout_deferred.callback(None)
            self.master.quit()


class PrePostTest:
    def __init__(self, session, words_file="words.json", images_folder="images"):
        self.session = session
        self.words_file = words_file
        self.images_folder = images_folder
        self.words = self.load_words()

    def load_words(self):
        if not os.path.exists(self.words_file):
            raise FileNotFoundError(f"Words file '{self.words_file}' not found.")
        with open(self.words_file, "r") as f:
            return json.load(f)

    def select_words(self, n=5):
        if len(self.words) < n:
            raise ValueError(f"Not enough words to select {n} unique items.")
        return random.sample(list(self.words.items()), n)

    @inlineCallbacks
    def conduct_test(self, selected_words, test_type="pre"):
        all_words = list(self.words.items())
        filler_words = [w for w in all_words if w not in selected_words]
        filler_imgs = [img for _, img in filler_words]
        trials = selected_words.copy()

        if test_type == "post":
            random.shuffle(trials)

        external_filler_imgs = [os.path.basename(p) for p in glob.glob(os.path.join(self.images_folder, "fillers", "*.*"))]
        results = []
        used_fillers = set()

        for i, (word, target_img) in enumerate(trials, 1):
            unused_fillers_available = [img for img in filler_imgs if img not in used_fillers]

            if len(unused_fillers_available) < 1:
                used_fillers.clear()
                unused_fillers_available = filler_imgs.copy()

            chosen_target_fillers = random.sample(unused_fillers_available, 1)
            used_fillers.update(chosen_target_fillers)

            available_fillers = [f for f in external_filler_imgs if f not in used_fillers]
            if len(available_fillers) < 2:
                used_fillers.clear()
                available_fillers = [f for f in external_filler_imgs if f not in used_fillers]

            chosen_fillers = random.sample(available_fillers, 2)
            used_fillers.update(chosen_fillers)

            images_shown = chosen_target_fillers + chosen_fillers + [target_img]
            random.shuffle(images_shown)

            while True:
                yield self.session.call("rie.dialogue.config.language", lang="en")
                yield self.session.call("rie.dialogue.say", text=word)

                root = tk.Tk()
                root.attributes('-fullscreen', True)
                root.attributes('-topmost', True)
                root.bind("<Escape>", lambda e: root.destroy())

                ui = PrePostTestUI(root, self.images_folder)
                selected_image = yield ui.show_images_with_timeout(images_shown, word)
                root.destroy()

                if selected_image is None:
                    continue
                
                correct = (selected_image == target_img)
                result = {
                    "trial": i,
                    "word": word,
                    "target_image": target_img,
                    "selected_image": selected_image,
                    "correct": correct,
                    "filler_images": filler_imgs
                }
                results.append(result)
                break

        return results

    def save_results(self, results, participant_num, game_version, test_type):
        # Construct folder path based on test_type
        folder_path = os.path.join("data", test_type)
        os.makedirs(folder_path, exist_ok=True)  # Create folder if it doesn't exist

        filename = f"results_{game_version}_participant_{participant_num}_{test_type}.json"
        full_path = os.path.join(folder_path, filename)

        with open(full_path, "w") as f:
            json.dump(results, f, indent=4)
