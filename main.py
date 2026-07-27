import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, font, colorchooser, simpledialog, messagebox
from PIL import Image, ImageTk

ARQUIVO_PERFIS = "perfis.json"

class BlocoDeNotasMonocromatico:
    def __init__(self, root):
        self.root = root
        self.root.title("Bloco de Notas Monográfico")
        self.root.geometry("900x650")
        self.root.configure(bg="#1e1e1e")

        self.wallpaper_caminho = None
        self.wallpaper_pil = None
        self.wallpaper_tk = None
        self.conteudo_texto = ""
        self.cor_texto = "#ffffff"
        self.fonte_nome = "Courier"
        self.fonte_tamanho = 12

        # Estilo TTK Monocromático
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("TLabel", background="#1e1e1e", foreground="#cccccc", font=("Courier", 10))
        self.style.configure("TButton", background="#2d2d2d", foreground="#ffffff", borderwidth=0, font=("Courier", 9, "bold"))
        self.style.map("TButton", background=[("active", "#404040")])

        # --- BARRA SUPERIOR (Minimalista) ---
        self.frame_topo = ttk.Frame(self.root, padding=8)
        self.frame_topo.pack(fill=tk.X)

        # Seleção de Fonte
        ttk.Label(self.frame_topo, text="FONTE:").pack(side=tk.LEFT, padx=(5, 2))
        self.combo_fonte = ttk.Combobox(self.frame_topo, values=list(font.families()), state="readonly", width=12)
        self.combo_fonte.set(self.fonte_nome)
        self.combo_fonte.pack(side=tk.LEFT, padx=5)
        self.combo_fonte.bind("<<ComboboxSelected>>", self.atualizar_fonte)

        # Tamanho da Fonte
        ttk.Label(self.frame_topo, text="TAM:").pack(side=tk.LEFT, padx=(5, 2))
        self.combo_tamanho = ttk.Combobox(self.frame_topo, values=[10, 12, 14, 16, 18, 20, 24, 28], state="readonly", width=4)
        self.combo_tamanho.set(str(self.fonte_tamanho))
        self.combo_tamanho.pack(side=tk.LEFT, padx=5)
        self.combo_tamanho.bind("<<ComboboxSelected>>", self.atualizar_fonte)

        # Botões do Editor
        btn_cor = ttk.Button(self.frame_topo, text="[ COR ]", command=self.escolher_cor_texto)
        btn_cor.pack(side=tk.LEFT, padx=3)

        btn_wallpaper = ttk.Button(self.frame_topo, text="[ WALLPAPER ]", command=self.definir_wallpaper)
        btn_wallpaper.pack(side=tk.LEFT, padx=3)

        btn_salvar = ttk.Button(self.frame_topo, text="[ SALVAR TXT ]", command=self.salvar_arquivo)
        btn_salvar.pack(side=tk.LEFT, padx=3)

        # --- SEÇÃO DE PERFIS DE TEMA ---
        ttk.Label(self.frame_topo, text="| PERFIL:").pack(side=tk.LEFT, padx=(10, 2))
        self.combo_perfis = ttk.Combobox(self.frame_topo, state="readonly", width=12)
        self.combo_perfis.pack(side=tk.LEFT, padx=3)
        self.combo_perfis.bind("<<ComboboxSelected>>", self.carregar_perfil_selecionado)

        btn_salvar_perfil = ttk.Button(self.frame_topo, text="[ + PERFIL ]", command=self.salvar_perfil)
        btn_salvar_perfil.pack(side=tk.LEFT, padx=3)

        # --- ÁREA PRINCIPAL (Canvas) ---
        self.canvas = tk.Canvas(self.root, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Texto Transparente no Canvas
        self.texto_id = self.canvas.create_text(
            30, 30,
            anchor="nw",
            text="Digite seu texto aqui...",
            fill=self.cor_texto,
            font=(self.fonte_nome, self.fonte_tamanho)
        )

        # Bindings de Evento
        self.root.bind("<Key>", self.ao_digitar)
        self.root.bind("<Control-s>", lambda event: self.salvar_arquivo())
        self.canvas.bind("<Configure>", self.ao_redimensionar)

        # Carregar lista de perfis salvos ao iniciar
        self.atualizar_lista_perfis()

    def atualizar_fonte(self, event=None):
        self.fonte_nome = self.combo_fonte.get()
        self.fonte_tamanho = int(self.combo_tamanho.get())
        self.canvas.itemconfig(self.texto_id, font=(self.fonte_nome, self.fonte_tamanho))

    def escolher_cor_texto(self):
        cor = colorchooser.askcolor(title="Escolha a cor do texto")
        if cor[1]:
            self.cor_texto = cor[1]
            self.canvas.itemconfig(self.texto_id, fill=self.cor_texto)

    def definir_wallpaper(self):
        caminho = filedialog.askopenfilename(
            parent=self.root,
            title="Selecione o Wallpaper",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if caminho:
            self.wallpaper_caminho = caminho
            self.wallpaper_pil = Image.open(caminho)
            self.redimensionar_e_desenhar_wallpaper()

    def redimensionar_e_desenhar_wallpaper(self):
        if self.wallpaper_pil:
            largura = self.canvas.winfo_width()
            altura = self.canvas.winfo_height()

            if largura > 10 and altura > 10:
                img_resized = self.wallpaper_pil.resize((largura, altura), Image.Resampling.LANCZOS)
                self.wallpaper_tk = ImageTk.PhotoImage(img_resized)

                self.canvas.delete("bg_img")
                self.canvas.create_image(0, 0, image=self.wallpaper_tk, anchor="nw", tags="bg_img")
                self.canvas.tag_lower("bg_img")

    def salvar_arquivo(self):
        caminho_arquivo = filedialog.asksaveasfilename(
            parent=self.root,
            title="Salvar Arquivo de Texto",
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        if caminho_arquivo:
            with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
                arquivo.write(self.conteudo_texto)

    # --- GERENCIAMENTO DE PERFIS DE TEMA ---
    def ler_perfis_json(self):
        if os.path.exists(ARQUIVO_PERFIS):
            try:
                with open(ARQUIVO_PERFIS, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def atualizar_lista_perfis(self):
        perfis = self.ler_perfis_json()
        nomes_perfis = list(perfis.keys())
        self.combo_perfis['values'] = nomes_perfis

    def salvar_perfil(self):
        nome_perfil = simpledialog.askstring("Novo Perfil", "Digite o nome para este perfil de tema:")
        if not nome_perfil:
            return

        perfis = self.ler_perfis_json()
        perfis[nome_perfil] = {
            "fonte_nome": self.fonte_nome,
            "fonte_tamanho": self.fonte_tamanho,
            "cor_texto": self.cor_texto,
            "wallpaper_caminho": self.wallpaper_caminho
        }

        with open(ARQUIVO_PERFIS, "w", encoding="utf-8") as f:
            json.dump(perfis, f, indent=4, ensure_ascii=False)

        self.atualizar_lista_perfis()
        self.combo_perfis.set(nome_perfil)
        messagebox.showinfo("Perfil Salvo", f"O perfil '{nome_perfil}' foi salvo com sucesso!")

    def carregar_perfil_selecionado(self, event=None):
        nome_perfil = self.combo_perfis.get()
        perfis = self.ler_perfis_json()

        if nome_perfil in perfis:
            dados = perfis[nome_perfil]
            
            # Aplicar fonte e tamanho
            self.fonte_nome = dados.get("fonte_nome", "Courier")
            self.fonte_tamanho = dados.get("fonte_tamanho", 12)
            self.combo_fonte.set(self.fonte_nome)
            self.combo_tamanho.set(str(self.fonte_tamanho))

            # Aplicar cor
            self.cor_texto = dados.get("cor_texto", "#ffffff")
            
            # Aplicar wallpaper
            self.wallpaper_caminho = dados.get("wallpaper_caminho")
            if self.wallpaper_caminho and os.path.exists(self.wallpaper_caminho):
                self.wallpaper_pil = Image.open(self.wallpaper_caminho)
                self.redimensionar_e_desenhar_wallpaper()
            else:
                self.canvas.delete("bg_img")
                self.wallpaper_pil = None

            # Atualizar estilo do texto
            self.canvas.itemconfig(self.texto_id, font=(self.fonte_nome, self.fonte_tamanho), fill=self.cor_texto)

    def ao_digitar(self, event):
        if event.state & 4:  
            return

        if event.keysym == "BackSpace":
            self.conteudo_texto = self.conteudo_texto[:-1]
        elif event.keysym == "Return":
            self.conteudo_texto += "\n"
        elif event.keysym == "Tab":
            self.conteudo_texto += "    "
        elif len(event.char) == 1 and ord(event.char) >= 32:
            self.conteudo_texto += event.char

        self.canvas.itemconfig(self.texto_id, text=self.conteudo_texto)

    def ao_redimensionar(self, event):
        self.redimensionar_e_desenhar_wallpaper()

if __name__ == "__main__":
    root = tk.Tk()
    app = BlocoDeNotasMonocromatico(root)
    root.mainloop()