from customtkinter import *
from funksjoner import resource_path
from tkinter import colorchooser, messagebox, simpledialog
from PIL import Image, ImageGrab
from tkinter.filedialog import asksaveasfilename, askopenfilename
import json

app = CTk()
app.title("Drawniverse V2")
app.geometry("1100x600")
set_appearance_mode("dark")

#Ikon for appen
app.iconbitmap(resource_path("Icons/appicon.ico"))


Utstyrlinjen = CTkFrame(app, height=100, bg_color="#293241")
Utstyrlinjen.pack(fill=X)

TegneLinjen = CTkFrame(app)
TegneLinjen.pack(fill=BOTH, expand=True)

Tegneark = CTkCanvas(TegneLinjen, bg="white")
Tegneark.pack(fill=BOTH, expand=True)


farge_blyanten = StringVar()
farge_blyanten.set("Black")

blyant_størrelse = IntVar()
blyant_størrelse.set(3)

Forrige_punkt = [0, 0]

# Legg til denne globale variabelen øverst i filen sammen med de andre
tegne_historie = []

#Dette er funksjoner som er i en Def
def Tegne(event):
    global Forrige_punkt
    x, y = event.x, event.y
    if Forrige_punkt != [0, 0]:
        linje = Tegneark.create_line(Forrige_punkt[0], Forrige_punkt[1], x, y,
                             fill=farge_blyanten.get(), width=blyant_størrelse.get(),
                             capstyle=ROUND, smooth=True)
        # Lagre streken i historien
        tegne_historie.append({
            'type': 'linje',
            'start': Forrige_punkt,
            'slutt': [x, y],
            'farge': farge_blyanten.get(),
            'størrelse': blyant_størrelse.get()
        })
    Forrige_punkt = [x, y]
def stopp_tegning(event):
    global Forrige_punkt
    Forrige_punkt = [0, 0]

def Viskelær(event):
    x, y = event.x, event.y
    radius = blyant_størrelse.get()  # Bruker verdien fra slideren for radius
    Tegneark.create_oval(x - radius, y - radius, x + radius, y + radius, fill="white", outline="white")
def aktiver_viskelær():
    farge_blyanten.set("White")
    Tegneark.config(cursor="dotbox")  # Indikerer viskelær-modus

def velg_farge():
    farge = colorchooser.askcolor()[1]
    if farge:
        farge_blyanten.set(farge)

def aktiver_dråpeteller():
    Tegneark.bind("<Button-1>", dråpeteller_funksjon)
    Tegneark.config(cursor="crosshair")
def dråpeteller_funksjon(event):
    x, y = event.x, event.y
    item = Tegneark.find_closest(x, y)
    if item:
        farge = Tegneark.itemcget(item, "fill")
        if farge:
            farge_blyanten.set(farge)
            Tilbake_til_pil_fra_knapp()
            Tegneark.unbind("<Button-1>")
            Tegneark.config(cursor="arrow")

def Tilbake_til_pil_fra_knapp():
    Tegneark.config(cursor="arrow")

def aktiver_blyant():
    farge_blyanten.set("Black")
    Tegneark.config(cursor="pencil")
    Tegneark.bind("<B1-Motion>", lambda event: Tegne(event))
    Tegneark.bind("<ButtonRelease-1>", stopp_tegning)
    Tegneark.unbind("<Button-1>")

def ny_fill():
    global tegne_historie
    tegne_historie = []  # Tøm historien
    Tegneark.delete("all")

def fyll_hele_arket():
    # Vis en advarsel før du fyller arket
    if not messagebox.askokcancel("Advarsel", "Dette vil slette alt på arket. Vil du fortsette?"):
        return

    farge = farge_blyanten.get()
    if not farge or farge == "White":
        messagebox.showwarning("Ingen farge valgt", "Vennligst velg en farge før du fyller arket.")
        return
    Tegneark.delete("all")
    Tegneark.create_rectangle(0, 0, Tegneark.winfo_width(), Tegneark.winfo_height(), fill=farge, outline=farge)

def lagre_fil():
    filbane = asksaveasfilename(defaultextension=".json", 
                               filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if filbane:
        with open(filbane, 'w', encoding='utf-8') as fil:
            json.dump(tegne_historie, fil, ensure_ascii=False, indent=2)
            messagebox.showinfo("Lagret", "Tegningen er lagret!")

def åpne_fil():
    global tegne_historie
    filbane = askopenfilename(defaultextension=".json", 
                             filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if filbane:
        try:
            with open(filbane, 'r', encoding='utf-8') as fil:
                tegne_historie = json.load(fil)
                tegn_fra_historie()
                messagebox.showinfo("Åpnet", "Tegningen er lastet!")
        except Exception as e:
            messagebox.showerror("Feil", f"Kunne ikke åpne filen: {str(e)}")

def tegn_fra_historie():
    Tegneark.delete("all")
    for strøk in tegne_historie:
        if strøk['type'] == 'linje':
            Tegneark.create_line(
                strøk['start'][0], strøk['start'][1],
                strøk['slutt'][0], strøk['slutt'][1],
                fill=strøk['farge'],
                width=strøk['størrelse'],
                capstyle=ROUND,
                smooth=True
            )
        elif strøk['type'] == 'tekst':
            Tegneark.create_text(
                strøk['posisjon'][0], strøk['posisjon'][1],
                text=strøk['tekst'],
                fill=strøk['farge'],
                font=("Arial", strøk['størrelse'])
            )

def lagre_som_bilde():
    filbane = asksaveasfilename(defaultextension=".png",
                               filetypes=[("PNG filer", "*.png"), ("Alle filer", "*.*")])
    if filbane:
        # Få koordinatene til tegneflaten
        x = Tegneark.winfo_rootx()
        y = Tegneark.winfo_rooty()
        w = Tegneark.winfo_width()
        h = Tegneark.winfo_height()
        
        # Ta et skjermbilde av tegneflaten
        skjermbilde = ImageGrab.grab(bbox=(x, y, x+w, y+h))
        skjermbilde.save(filbane)
        messagebox.showinfo("Lagret", "Bildet er lagret!")

def lagre_fil_med_format(format_type):
    if format_type == "JSON":
        lagre_fil()
    elif format_type == "PNG":
        lagre_som_bilde()
    elif format_type == "JPG":
        filbane = asksaveasfilename(defaultextension=".jpg",
                                   filetypes=[("JPG filer", "*.jpg"), ("Alle filer", "*.*")])
        if filbane:
            x = Tegneark.winfo_rootx()
            y = Tegneark.winfo_rooty()
            w = Tegneark.winfo_width()
            h = Tegneark.winfo_height()
            
            skjermbilde = ImageGrab.grab(bbox=(x, y, x+w, y+h))
            skjermbilde = skjermbilde.convert('RGB')  # Konverter til RGB for JPG
            skjermbilde.save(filbane, quality=95)
            messagebox.showinfo("Lagret", "Bildet er lagret som JPG!")

def legg_til_tekst(event):
    x, y = event.x, event.y
    tekst = simpledialog.askstring("Skriv tekst", "Skriv inn teksten:")
    if tekst:
        Tegneark.create_text(x, y, text=tekst, fill=farge_blyanten.get(), font=("Arial", blyant_størrelse.get()))
        # Lagre teksten i historien
        tegne_historie.append({
            'type': 'tekst',
            'posisjon': [x, y],
            'tekst': tekst,
            'farge': farge_blyanten.get(),
            'størrelse': blyant_størrelse.get()
        })
        # Gå tilbake til blyant-modus etter at teksten er lagt til
        aktiver_blyant()

def aktiver_tekst():
    Tegneark.config(cursor="xterm")
    Tegneark.bind("<Button-1>", legg_til_tekst)
    Tegneark.bind("<Button-3>", lambda e: Tilbake_til_normal_modus())

def Tilbake_til_normal_modus():
    Tegneark.config(cursor="arrow")
    Tegneark.unbind("<Button-1>")
    Tegneark.bind("<B1-Motion>", lambda event: Tegne(event))
    Tegneark.bind("<ButtonRelease-1>", stopp_tegning)

#Klapper

Blyant_icon = CTkImage(Image.open(resource_path("Icons/Blyant_icon.png")), size=(20, 20))
BlyantButton = CTkButton(Utstyrlinjen, image=Blyant_icon, command=aktiver_blyant, text="", width=60, height=30, corner_radius=32,  hover_color="#C850C0", fg_color="#293241")
BlyantButton.grid(row=0, column=0, padx=10, pady=5)

Viskelær_icon = CTkImage(Image.open(resource_path("Icons/Eraser_icon.png")), size=(20, 20))
Viskelærbutton = CTkButton(Utstyrlinjen, image=Viskelær_icon, command=aktiver_viskelær, text="", width=60, height=30, corner_radius=32,  hover_color="#C850C0", fg_color="#293241")
Viskelærbutton.grid(row=0, column=1, padx=10, pady=5)

Dråpeteller_icon = CTkImage(Image.open(resource_path("Icons/Dropper_icon.png")), size=(20, 20))
DråpetellerButton = CTkButton(Utstyrlinjen, image=Dråpeteller_icon, command=aktiver_dråpeteller, text="", width=60, height=30, corner_radius=32,  hover_color="#C850C0", fg_color="#293241")
DråpetellerButton.grid(row=0, column=2, padx=10, pady=5)

Fargevelger_icon = CTkImage(Image.open(resource_path("Icons/Color_icon.png")), size=(20, 20))
FargevelgerButton = CTkButton(Utstyrlinjen, image=Fargevelger_icon, command=velg_farge, text="", width=60, height=30, corner_radius=32,  hover_color="#C850C0", fg_color="#293241")
FargevelgerButton.grid(row=0, column=3, padx=10, pady=5)

Fyll_ark_icon = CTkImage(Image.open(resource_path("Icons/Fill_icon.png")), size=(20, 20))
FyllButton = CTkButton(Utstyrlinjen, image=Fyll_ark_icon, command=fyll_hele_arket, text="", width=60, height=30, corner_radius=32,  hover_color="#C850C0", fg_color="#293241")
FyllButton.grid(row=0, column=4, padx=10, pady=5)

Nyfill_icon = CTkImage(Image.open(resource_path("Icons/Nyfil.png")), size=(20, 20))
NyfilButton = CTkButton(Utstyrlinjen, image=Nyfill_icon, command=ny_fill, text="New Canvas", width=60, height=30, corner_radius=32,  hover_color="#C850C0", fg_color="#293241")
NyfilButton.grid(row=0, column=6, padx=10, pady=6)

Tekst_icon = CTkImage(Image.open(resource_path("Icons/Text_icon.png")), size=(20, 20))
TekstButton = CTkButton(Utstyrlinjen, image=Tekst_icon, command=aktiver_tekst, text="", width=60, height=30, corner_radius=32, hover_color="#C850C0", fg_color="#293241")
TekstButton.grid(row=0, column=5, padx=10, pady=5)

størrelse_slider = CTkSlider(master=app, from_=1, to=40, variable=blyant_størrelse, orientation="horizontal", width=200, corner_radius=32, fg_color="#293241",)
størrelse_slider.pack(pady=20)

Åpne_icon = CTkImage(Image.open(resource_path("Icons/Open.png")), size=(20, 20))
ÅpneButton = CTkButton(Utstyrlinjen, image=Åpne_icon, command=åpne_fil, text="Open", width=60, height=30, corner_radius=32, hover_color="#C850C0", fg_color="#293241")
ÅpneButton.grid(row=0, column=7, padx=10, pady=5)

Lagre_icon = CTkImage(Image.open(resource_path("Icons/Save.png")), size=(20, 20))
lagrings_alternativer = ["JSON", "PNG", "JPG"]
Lagre_dropdown = CTkOptionMenu(Utstyrlinjen, values=lagrings_alternativer, command=lagre_fil_med_format, width=100, height=30, corner_radius=32, fg_color="#293241", button_color="#293241", button_hover_color="#C850C0", dynamic_resizing=False)
Lagre_dropdown.grid(row=0, column=8, padx=10, pady=5)
Lagre_dropdown.set("Lagre som")

# Datamus
Tegneark.bind("<B1-Motion>", lambda event: Tegne(event))
Tegneark.bind("<ButtonRelease-1>", stopp_tegning)
app.bind("<Delete>", lambda event: ny_fill())
app.bind("<Control-f>", lambda event: velg_farge())
app.bind("<Control-b>", lambda event: fyll_hele_arket())

def avslutt_program():
    if messagebox.askyesnocancel("Avslutt", "Vil du lagre før du avslutter?"):
        # Spør om formatet de vil lagre i
        format_type = messagebox.askquestion("Lagre format", "Vil du lagre som et bilde (PNG) eller JSON?", icon='question', type='yesno')
        if format_type == 'yes':
            lagre_som_bilde()
        else:
            lagre_fil()
    app.destroy()

# Legg til denne linjen for å fange opp lukkebegivenheten
app.protocol("WM_DELETE_WINDOW", avslutt_program)

# Kjører hovedløkke
app.mainloop()