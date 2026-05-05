import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
from tkcalendar import DateEntry

# --- Настройки ---
CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Быт", "Здоровье"]
DATA_FILE = "expenses.json"

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("900x650")
        self.expenses = []
        self.load_data()
        self.create_widgets()

    def create_widgets(self):
        # --- Виджеты ввода ---
        frame_input = ttk.LabelFrame(self.root, text="Добавить расход")
        frame_input.pack(pady=10, fill="x")

        ttk.Label(frame_input, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_amount = ttk.Entry(frame_input, width=15)
        self.entry_amount.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_input, text="Категория:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.combo_category = ttk.Combobox(frame_input, values=CATEGORIES, state="readonly", width=15)
        self.combo_category.current(0)
        self.combo_category.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_input, text="Дата:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.entry_date = DateEntry(frame_input, date_pattern='dd.MM.yyyy')
        self.entry_date.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(frame_input, text="Добавить расход", command=self.add_expense).grid(row=0, column=6, padx=10)

        # --- Таблица расходов ---
        columns = ("date", "category", "amount")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("category", text="Категория")
        self.tree.heading("amount", text="Сумма ₽")
        
        self.tree.column("date", width=120)
        self.tree.column("category", width=150)
        self.tree.column("amount", width=100, anchor="e")
        
        self.tree.pack(expand=True, fill="both", pady=10)

        # --- Панель инструментов (Фильтры и Сумма) ---
        frame_tools = ttk.Frame(self.root)
        frame_tools.pack(pady=10, fill="x")

        # Фильтр по категории
        ttk.Label(frame_tools, text="Фильтр по категории:").pack(side="left", padx=(0, 5))
        self.filter_combo = ttk.Combobox(frame_tools, values=["Все"] + CATEGORIES, state="readonly", width=12)
        self.filter_combo.current(0)
        self.filter_combo.pack(side="left", padx=(0, 15))
        
        ttk.Button(frame_tools, text="Фильтровать", command=self.filter_expenses).pack(side="left", padx=(0, 20))

        # Подсчёт суммы за период
        ttk.Label(frame_tools, text="Период для суммы:").pack(side="left", padx=(20, 5))
        
        self.start_date_sum = DateEntry(frame_tools, date_pattern='dd.MM.yyyy', width=12)
        self.start_date_sum.pack(side="left", padx=(0, 5))
        
        ttk.Label(frame_tools, text="—").pack(side="left")
        
        self.end_date_sum = DateEntry(frame_tools, date_pattern='dd.MM.yyyy', width=12)
        self.end_date_sum.pack(side="left", padx=(5, 15))
        
        ttk.Button(frame_tools, text="Сумма за период", command=self.sum_period).pack(side="left", padx=(0, 20))

        # Кнопки сохранения/загрузки
        save_frame = ttk.Frame(self.root)
        save_frame.pack(pady=5)
        ttk.Button(save_frame, text="💾 Сохранить данные", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(save_frame, text="📂 Загрузить данные", command=self.load_data).pack(side="left", padx=5)
         
    def load_data(self):
        """Загрузка данных из JSON-файла."""
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Преобразуем строковые даты обратно в объекты datetime для внутренних расчетов
                for item in data:
                    item['date_obj'] = datetime.strptime(item['date'], '%d.%m.%Y')
                self.expenses = data
                self.update_tree()
                print("Данные загружены.")
        except FileNotFoundError:
            print("Файл данных не найден. Будет создан новый.")
            self.expenses = []
            self.update_tree()
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка файла", "Файл данных поврежден. Будет создан новый файл.")
            self.expenses = []
            self.update_tree()
    
    def save_data(self):
        """Сохранение данных в JSON-файл."""
        try:
            # Создаем копию списка без объектов datetime (сохраняем только строки)
            data_to_save = []
            for expense in self.expenses:
                save_item = {
                     'date': expense['date'],
                     'category': expense['category'],
                     'amount': expense['amount']
                 }
                data_to_save.append(save_item)
             
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", "Данные успешно сохранены!")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить файл: {e}")
    
    def add_expense(self):
        """Добавление нового расхода после валидации."""
         
        # Валидация: Проверка на пустую строку и пробелы
        amount_str = self.entry_amount.get().strip()
        if not amount_str:
            messagebox.showerror("Ошибка ввода", "Поле 'Сумма' не может быть пустым.")
            return

        # Валидация суммы (число и > 0)
        try:
            amount = float(amount_str.replace(',', '.'))
            if amount <= 0:
                raise ValueError("Сумма должна быть больше нуля.")
        except ValueError as e:
            messagebox.showerror("Ошибка ввода суммы", str(e))
            return

        category = self.combo_category.get()
         
        # Валидация даты (должна быть выбрана)
        date_obj = self.entry_date.get_date()
        date_str = date_obj.strftime('%d.%m.%Y')
         
        # Добавление в список и таблицу (храним и строку для отображения/JSON и объект для расчетов)
        expense = {
             "date": date_str,
             "category": category,
             "amount": round(amount, 2),
             "date_obj": date_obj
         }
         
        self.expenses.append(expense)
         
        self.update_tree()
         
        # Очистка полей для следующего ввода
        self.entry_amount.delete(0, tk.END)
        self.combo_category.current(0)
        self.entry_date.set_date(datetime.now())
             
    def update_tree(self):
        """Полная перерисовка таблицы Treeview."""
        for i in self.tree.get_children():
            self.tree.delete(i)
             
        for expense in sorted(self.expenses, key=lambda x: x['date_obj'], reverse=True):
            self.tree.insert("", tk.END,
                              values=(expense["date"], expense["category"], f"{expense['amount']:.2f}"))
             
    def filter_expenses(self):
        """Фильтрация таблицы по выбранной категории."""
        selected = self.filter_combo.get()
         
        for i in self.tree.get_children():
            self.tree.delete(i)
             
        if selected == "Все":
            filtered_list = self.expenses
        else:
            filtered_list = [e for e in self.expenses if e["category"] == selected]
             
        for expense in sorted(filtered_list, key=lambda x: x['date_obj'], reverse=True):
            self.tree.insert("", tk.END,
                              values=(expense["date"], expense["category"], f"{expense['amount']:.2f}"))
                 
    def sum_period(self):
        """Подсчёт суммы расходов за выбранный период."""
        start = self.start_date_sum.get_date()
        end = self.end_date_sum.get_date()
          
        total = sum(expense['amount'] for expense in self.expenses 
                     if start <= expense['date_obj'] <= end)
                      
        messagebox.showinfo("Итог за период", 
                             f"Сумма расходов с {start.strftime('%d.%m.%Y')} по {end.strftime('%d.%m.%Y')} составляет: {total:.2f} ₽")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()