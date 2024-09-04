import codecs
import os
import re as regex
import tkinter
from tkinter import Tk, filedialog, messagebox, ttk

selected_folder = os.getcwd()
png_dict = dict()
png_count = 1
kks_card_dict = dict()
converted_root_folder_name = ""
do_convert_default = True


def get_files_dict(folder_path):
    new_dict = dict()
    for path, _, files in os.walk(folder_path):
        new_list = []
        for filename in files:
            if regex.match(r".*(\.png)$", filename):
                new_list.append(filename)
        relative_path = os.path.relpath(path, folder_path)
        new_dict[relative_path] = new_list

    return new_dict


def check_png(card_path):
    with codecs.open(card_path, "rb") as card:
        data = card.read()
        card_type = 0
        if data.find(b"KoiKatuChara") != -1:
            card_type = 1
            if data.find(b"KoiKatuCharaSP") != -1:
                card_type = 2
            elif data.find(b"KoiKatuCharaSun") != -1:
                card_type = 3
        print(f"[{card_type}] {card_path}")
    return card_type


def do_convert_check_event():
    print(f"convert = {do_convert.get()}")


def convert_kk(card_name, source_card_path, target_folder_path):
    with codecs.open(source_card_path, mode="rb") as card:
        data = card.read()

        replace_list = [
            [b"\x15\xe3\x80\x90KoiKatuCharaSun", b"\x12\xe3\x80\x90KoiKatuChara"],
            [b"Parameter\xa7version\xa50.0.6", b"Parameter\xa7version\xa50.0.5"],
            [b"version\xa50.0.6\xa3sex", b"version\xa50.0.5\xa3sex"],
        ]

        for text in replace_list:
            data = data.replace(text[0], text[1])

        if not os.path.isdir(target_folder_path):
            os.makedirs(target_folder_path)
        new_file_path = os.path.normpath(os.path.join(target_folder_path, card_name))

        # print(f"new_file_path {new_file_path}")

        with codecs.open(new_file_path, "wb") as new_card:
            new_card.write(data)


def c_get_list():
    global selected_folder, png_dict, png_count, png_count_t, converted_root_folder_name
    b_sel["state"] = "disabled"
    selected_folder = filedialog.askdirectory(
        title="Select target path (folder contain cards)", mustexist=True
    )

    if selected_folder:
        print(f"path: {selected_folder}")
        os.chdir(selected_folder)
        converted_root_folder_name = "kk_" + os.path.basename(selected_folder)
    else:
        print("no path")
        b_sel["state"] = "normal"
        return

    png_dict = get_files_dict(selected_folder)
    png_count = 0
    for pngs in png_dict.values():
        png_count += len(pngs)
    png_count_t.set(f"png found: {png_count}")

    if png_count > 0:
        b_p["state"] = "normal"
    else:
        b_p["state"] = "disabled"

    b_sel["state"] = "normal"


def process_png():
    global selected_folder, png_dict, converted_root_folder_name, kks_card_dict, window, png_count, png_count_t

    count = len(png_dict)
    if count > 0:
        bar = ttk.Progressbar(window, maximum=count, length=250)
        bar.pack(pady=10)
        bar_val = 0
        print("0: unknown / 1: kk / 2: kksp / 3: kks")
        for relpath, png_list in png_dict.items():
            kks_card_list = []
            for png in png_list:
                if check_png(os.path.join(selected_folder, relpath, png)) == 3:
                    kks_card_list.append(png)
                bar_val = bar_val + 1
                bar["value"] = bar_val
                window.update()
            kks_card_dict[relpath] = kks_card_list
        bar.destroy()
    else:
        messagebox.showinfo("Done", f"no PNG found")
        return

    count = 0
    for cards in kks_card_dict.values():
        count += len(cards)
    if count > 0:
        print(kks_card_dict)

        converted_root_path = os.path.normpath(
            os.path.join(os.path.dirname(selected_folder), converted_root_folder_name)
        )
        print(f"converted_root_path: {converted_root_path}")

        is_convert = do_convert.get()
        if is_convert:
            print(f"do convert is [{is_convert}]")
            if not os.path.isdir(converted_root_path):
                os.mkdir(converted_root_path)

        for relpath, cards in kks_card_dict.items():
            for card in cards:
                source_card_path = os.path.normpath(
                    os.path.join(selected_folder, relpath, card)
                )
                target_folder_path = os.path.normpath(
                    os.path.join(converted_root_path, relpath)
                )

                if is_convert:
                    convert_kk(card, source_card_path, target_folder_path)

        if is_convert:
            messagebox.showinfo(
                "Done",
                f'[{count}] cards\nfrom "{selected_folder}" folder\nconvert and save to "{converted_root_folder_name}" folder',
            )
        else:
            messagebox.showinfo(
                "Done", f"[{count}] cards\nmove to [{selected_folder}] folder"
            )
    else:
        messagebox.showinfo("Done", f"no KKS card found")

    # reset
    png_dict = []
    kks_card_dict = []
    png_count = 0
    png_count_t.set(f"png found: 0")
    b_p["state"] = "disabled"


window = Tk()
# window.withdraw()
window.title("KKSCF")
w = 300
h = 350
ltx = int((window.winfo_screenwidth() - w) / 2)
lty = int((window.winfo_screenheight() - h) / 2)
window.geometry(f"{w}x{h}+{ltx}+{lty}")

tkinter.Label(window, text=" ", pady=5).pack()

b_sel = tkinter.Button(
    window,
    text="Select folder contain cards",
    padx=10,
    pady=10,
    relief="raised",
    bd=3,
    command=c_get_list,
)
b_sel.pack()

tkinter.Label(window, text=" ", pady=5).pack()

png_count_t = tkinter.StringVar()
png_count_t.set(f"png found: {png_count}")
tkinter.Label(window, textvariable=png_count_t, pady=10).pack()

tkinter.Label(window, text=" ", pady=5).pack()

do_convert = tkinter.BooleanVar()
do_convert.set(do_convert_default)
do_convert_check = tkinter.Checkbutton(
    window,
    text="copy & convert KKS to KK",
    variable=do_convert,
    command=do_convert_check_event,
)
do_convert_check.pack()

tkinter.Label(window, text=" ", pady=5).pack()

b_p = tkinter.Button(
    window, text="Process", relief="raised", padx=10, pady=10, bd=3, command=process_png
)
b_p.pack()
b_p["state"] = "disabled"

tkinter.Label(window, text=" ", pady=5).pack()

window.mainloop()
exit(0)
