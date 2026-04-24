import tkinter as tk
from tkinter import messagebox


class GuiView:
    def __init__(self, controller):
        self.controller = controller

        #  crear la ventana raíz
        self.root = tk.Tk()
        self.root.title("Risk Evaluator Pro")
        self.root.geometry("950x600")
       # frames (pantallas)
        self.frame_select = tk.Frame(self.root)
        self.frame_menu = tk.Frame(self.root)
        self.frame_edit = tk.Frame(self.root)
        self.frame_controls = tk.Frame(self.root)
        self.frame_analysis = tk.Frame(self.root)   # ← ESTA LÍNEA ES CLAVE

        for frame in (
            self.frame_select,
            self.frame_menu,
            self.frame_edit,
            self.frame_controls,
            self.frame_analysis
        ):
            frame.grid(row=0, column=0, sticky="nsew")

        #construir pantallas
        self._build_select_frame()
        self._build_menu_frame()
        self._build_edit_frame()
        self._build_controls_frame()
        self._build_analysis_frame()
        #mostrar la pantalla
        self.show_frame(self.frame_select)


    # ==========================================================
    # NAVEGACIÓN
    # ==========================================================

    def show_frame(self, frame):
        frame.tkraise()

    # ==========================================================
    # PANTALLA 1 – SELECCIÓN DE RIESGOS
    # ==========================================================

    def _build_select_frame(self):
        tk.Label(
            self.frame_select,
            text="Company Risk Selection",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        tk.Label(
            self.frame_select,
            text="Select the risks applicable to your company",
            font=("Arial", 11)
        ).pack(pady=5)

        self.vars_active = {}

        list_frame = tk.Frame(self.frame_select)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        canvas = tk.Canvas(list_frame)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for risk_id, risk in self.controller.risks.items():
            cr = self.controller.company_assessment.company_risks[risk_id]
            var = tk.BooleanVar(value=cr.is_active())
            self.vars_active[risk_id] = var

            tk.Checkbutton(
                scroll_frame,
                text=f"{risk.name} ({risk.risk_type.name})",
                variable=var,
                command=lambda r=risk_id, v=var: self._toggle_risk(r, v)
            ).pack(anchor="w", pady=2)

        tk.Button(
            self.frame_select,
            text="Confirm selection",
            width=25,
            command=lambda: self.show_frame(self.frame_menu)
        ).pack(pady=15)

    def _toggle_risk(self, risk_id, var):
        self.controller.company_assessment.set_risk_active(risk_id, var.get())

    # ==========================================================
    # PANTALLA 2 – MENÚ PRINCIPAL
    # ==========================================================

    def _build_menu_frame(self):
        tk.Label(
            self.frame_menu,
            text="Risk Assessment",
            font=("Arial", 16, "bold")
        ).pack(pady=20)

        tk.Label(
            self.frame_menu,
            text="What would you like to do?",
            font=("Arial", 12)
        ).pack(pady=10)

        tk.Button(
            self.frame_menu,
            text="Edit risk selection",
            width=35,
            command=lambda: self.show_frame(self.frame_select)
        ).pack(pady=10)

        tk.Button(
            self.frame_menu,
            text="Edit criticalities",
            width=35,
            command=self._enter_edit_frame
        ).pack(pady=10)

        tk.Button(
            self.frame_menu,
            text="Mark controls",
            width=35,
            command=self._enter_controls_frame
        ).pack(pady=10)
        tk.Button(
            self.frame_menu,
            text="Next → Analysis",
            width=35,
            command=self._enter_analysis_frame
        ).pack(pady=20)
        tk.Button(
            self.frame_menu,
            text="Exit",
            width=35,
            command=self.root.quit
        ).pack(pady=30)


    # ==========================================================
    # PANTALLA 3 – EDICIÓN DE CRITICIDADES
    # ==========================================================
    def _build_scale_help(self, parent):
        frame = tk.LabelFrame(
            parent,
            text="Scale Guide (1–5)",
            padx=10,
            pady=5
        )
        frame.pack(fill="x", pady=10)

        text = (
            "Probability:\n"
            "  1 – Very unlikely\n"
            "  2 – Unlikely\n"
            "  3 – Possible\n"
            "  4 – Likely\n"
            "  5 – Very likely\n\n"
            "Impact (financial / operational / reputational):\n"
            "  1 – Minimal impact\n"
            "  2 – Low impact\n"
            "  3 – Moderate impact\n"
            "  4 – High impact\n"
            "  5 – Critical impact"
        )

        tk.Label(
            frame,
            text=text,
            justify="left",
            font=("Arial", 9)
        ).pack(anchor="w")

    def _build_edit_frame(self):
        tk.Label(
            self.frame_edit,
            text="Edit Criticalities",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        main = tk.Frame(self.frame_edit)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        left = tk.Frame(main, width=300)
        left.pack(side="left", fill="y")

        tk.Label(left, text="Active Risks", font=("Arial", 12, "bold")).pack(pady=5)

        self.listbox = tk.Listbox(left, height=20)
        self.listbox.pack(fill="y", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self._on_select_risk)

        right = tk.Frame(main)
        right.pack(side="right", fill="both", expand=True, padx=20)

        self.lbl_edit = tk.Label(right, text="Select a risk to edit")
        self.lbl_edit.pack(pady=10)

        self.spin_p = self._spinbox(right, "Probability")
        self.spin_if = self._spinbox(right, "Financial Impact")
        self.spin_io = self._spinbox(right, "Operational Impact")
        self.spin_ir = self._spinbox(right, "Reputational Impact")
        self._build_scale_help(right)


        btns = tk.Frame(right)
        btns.pack(pady=20)

        self.btn_apply = tk.Button(
            btns,
            text="Apply",
            width=15,
            command=self._apply_changes,
            state="disabled"
        )
        self.btn_apply.pack(side="left", padx=10)

        tk.Button(
            btns,
            text="Back",
            width=15,
            command=lambda: self.show_frame(self.frame_menu)
        ).pack(side="right", padx=10)

    # ==========================================================
    # PANTALLA 4 – MARCADO DE FORTALEZAS
    # ==========================================================

    def _build_controls_frame(self):
        tk.Label(
            self.frame_controls,
            text="Mark Controls",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        main = tk.Frame(self.frame_controls)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        left = tk.Frame(main, width=300)
        left.pack(side="left", fill="y")

        tk.Label(left, text="Active Risks", font=("Arial", 12, "bold")).pack(pady=5)

        self.listbox_ctrl = tk.Listbox(left, height=20)
        self.listbox_ctrl.pack(fill="y", expand=True)
        self.listbox_ctrl.bind("<<ListboxSelect>>", self._on_select_risk_controls)

        self.ctrl_right = tk.Frame(main)
        self.ctrl_right.pack(side="right", fill="both", expand=True, padx=20)

        tk.Button(
            self.frame_controls,
            text="Back",
            width=20,
            command=lambda: self.show_frame(self.frame_menu)
        ).pack(pady=10)
    # ==========================================================
    # PANTALLA 5 – Analisis
    # ==========================================================
    def _build_analysis_frame(self):
        tk.Label(
            self.frame_analysis,
            text="Risk Analysis",
            font=("Arial", 16, "bold")
        ).pack(pady=20)

        tk.Button(
            self.frame_analysis,
            text="View inherent risk",
            width=35,
            command=self._show_inherent_risk
        ).pack(pady=10)

        tk.Button(
            self.frame_analysis,
            text="View residual risk",
            width=35,
            command=self._show_residual_risk
        ).pack(pady=10)

        tk.Button(
            self.frame_analysis,
            text="Risk ranking",
            width=35,
            command=self._show_ranking
        ).pack(pady=10)

        tk.Button(
            self.frame_analysis,
            text="Back",
            width=35,
            command=lambda: self.show_frame(self.frame_menu)
        ).pack(pady=30)
    def _enter_analysis_frame(self):
            self.show_frame(self.frame_analysis)

    def _show_inherent_risk(self):
        assessment = self.controller.company_assessment
        risks = assessment.get_active_risks()

        if not risks:
            messagebox.showinfo(
                "Inherent risk",
                "No active risks selected."
            )
            return
        text = "Inherent risk by risk:\n\n"

        for cr in risks:
            value = cr.calculate_inherent_risk()
            level = cr.risk_level(value)
            text += f"- {cr.base_risk.name}: {value:.2f} ({level})\n"

        messagebox.showinfo("Inherent risk", text)

    def _show_residual_risk(self):
        assessment = self.controller.company_assessment
        risks = assessment.get_active_risks()

        if not risks:
            messagebox.showinfo(
                "Residual risk",
                "No active risks selected."
            )
            return

        text = "Residual risk by risk:\n\n"

        for cr in risks:
            value = cr.calculate_residual_risk()
            level = cr.risk_level(value)
            controls_count = len(cr.enabled_controls)

            text += (
                f"- {cr.base_risk.name}: {value:.2f} ({level}) "
                f"[controls: {controls_count}]\n"
            )

        messagebox.showinfo("Residual risk", text)

    def _show_ranking(self):
        assessment = self.controller.company_assessment
        ranking = assessment.get_risk_ranking(residual=True)

        if not ranking:
            messagebox.showinfo(
                "Risk ranking",
                "No active risks selected."
            )
            return

        text = "Risk ranking (residual risk):\n\n"

        for i, cr in enumerate(ranking, start=1):
            value = cr.calculate_residual_risk()
            level = cr.risk_level(value)
            text += f"{i}. {cr.base_risk.name}: {value:.2f} ({level})\n"

        messagebox.showinfo("Risk ranking", text)

    # ==========================================================
    # LÓGICA
    # ==========================================================

    def _enter_edit_frame(self):
        self._load_active_risks(self.listbox)
        self.show_frame(self.frame_edit)

    def _enter_controls_frame(self):
        self._load_active_risks(self.listbox_ctrl)
        self.show_frame(self.frame_controls)

    def _load_active_risks(self, listbox):
        listbox.delete(0, tk.END)
        self.active_risk_ids = []

        for cr in self.controller.company_assessment.get_active_risks():
            listbox.insert(tk.END, cr.base_risk.name)
            self.active_risk_ids.append(cr.base_risk.risk_id)

    def _on_select_risk(self, event):
        if not self.listbox.curselection():
            return

        idx = self.listbox.curselection()[0]
        cr = self.controller.company_assessment.company_risks[self.active_risk_ids[idx]]

        self.selected_risk_id = cr.base_risk.risk_id
        self.lbl_edit.config(text=f"Editing: {cr.base_risk.name}")

        self._set_spin(self.spin_p, cr.custom_probability)
        self._set_spin(self.spin_if, cr.custom_impact_financial)
        self._set_spin(self.spin_io, cr.custom_impact_operational)
        self._set_spin(self.spin_ir, cr.custom_impact_reputational)

        self.btn_apply.config(state="normal")

    def _on_select_risk_controls(self, event):
        if not self.listbox_ctrl.curselection():
            return

        for w in self.ctrl_right.winfo_children():
            w.destroy()

        idx = self.listbox_ctrl.curselection()[0]
        cr = self.controller.company_assessment.company_risks[self.active_risk_ids[idx]]

        tk.Label(
            self.ctrl_right,
            text=f"Controls for {cr.base_risk.name}",
            font=("Arial", 12, "bold")
        ).pack(pady=5)

        self.ctrl_vars = {}

        for cid, control in cr.base_risk.controls.items():
            var = tk.BooleanVar(value=cid in cr.enabled_controls)
            self.ctrl_vars[cid] = var

            tk.Checkbutton(
                self.ctrl_right,
                text=control.name,
                variable=var
            ).pack(anchor="w")

        tk.Button(
            self.ctrl_right,
            text="Aplicar",
            command=lambda: self._apply_controls(cr)
        ).pack(pady=10)

    def _apply_controls(self, cr):
        cr.enabled_controls.clear()
        for cid, var in self.ctrl_vars.items():
            if var.get():
                cr.enabled_controls[cid] = cr.base_risk.controls[cid]

        messagebox.showinfo("Done", "Controls updated successfully")

    def _spinbox(self, parent, label):
        frame = tk.Frame(parent)
        frame.pack(anchor="w", pady=4)

        tk.Label(frame, text=label, width=30, anchor="w").pack(side="left")
        spin = tk.Spinbox(frame, from_=1, to=5, width=5)
        spin.pack(side="left")
        return spin

    def _set_spin(self, spin, value):
        spin.delete(0, "end")
        spin.insert(0, value)

    def _apply_changes(self):
        if not self.selected_risk_id:
            return

        cr = self.controller.company_assessment.company_risks[self.selected_risk_id]
        cr.set_custom_scores(
            int(self.spin_p.get()),
            int(self.spin_if.get()),
            int(self.spin_io.get()),
            int(self.spin_ir.get())
        )

        messagebox.showinfo("Done", "Changes applied successfully")

    # ==========================================================
    # RUN
    # ==========================================================

    def run(self):
        self.root.mainloop()
