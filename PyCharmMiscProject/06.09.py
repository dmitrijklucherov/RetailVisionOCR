import csv
import psycopg

# =====================================================================
# ШАГ 1: ЧТЕНИЕ ФАЙЛА С ДИСКА (Канал проверен экспертизой)
# =====================================================================
with open("my_file.csv", mode="r", encoding="utf-8") as file_handler:
    reader = csv.reader(file_handler)
    next(reader)  # Пропустили шапку
    file_rows = list(reader)


# =====================================================================
# ШАГ 2: КЛАСС ОЧИСТКИ (Инкапсуляция строго по карте колонок)
# =====================================================================
class MarketFilter:
    def __init__(self, rank, peak, all_peak, act_gross, adj_gross, artist, title_tour, title_years, shows, av_gross):
        # Первые три колонки (если пусто — ставим 1)
        self.rank = int(rank.strip()) if rank.strip() else 1
        self.peak = int(peak.split("[")[0]) if peak else 0
        self.all_peak = int(all_peak.split("[")[0]) if all_peak else 0

        # 🌟 ИСПРАВЛЕНО: сначала .strip(), а потом .split("[")[0]!
        if act_gross.strip():
            clean_act = act_gross.replace("$", "").replace(",", "").strip().split("[")[0]
            self.act_gross = int(clean_act) if clean_act else 0
        else:
            self.act_gross = 0

        # 🌟 ИСПРАВЛЕНО: сначала .strip(), а потом .split("[")[0]!
        if adj_gross.strip():
            clean_agj = adj_gross.replace("$", "").replace(",", "").strip().split("[")[0]
            self.adj_gross = int(clean_agj) if clean_agj else 0
        else:
            self.adj_gross = 0

        # Текстовые поля (тоже исправили порядок методов!)
        self.artist = artist.strip().split("[")[0]
        self.title_tour = title_tour.replace("*", "").strip().split("[")[0]
        self.title_years = title_years.replace("вЂ“", "-").strip()

        self.shows = int(shows.strip()) if shows.strip() else 0

        # 🌟 ИСПРАВЛЕНО: сначала .strip(), а потом .split("[")[0]!
        if av_gross.strip():
            clean_av = av_gross.replace("$", "").replace(",", "").strip().split("[")[0]
            self.av_gross = int(clean_av) if clean_av else 0
        else:
            self.av_gross = 0
    # Проверьте, чтобы внутри класса MarketFilter была написана эта функция:
    def ret_filter(self):
        return (self.rank, self.peak, self.all_peak, self.act_gross, self.adj_gross,
                self.artist, self.title_tour, self.title_years, self.shows, self.av_gross)



# =====================================================================
# ШАГ 3: ООП-УПРАВЛЕНЕЦ БАЗОЙ ДАННЫХ
# =====================================================================
class Connect:
    def __init__(self):
        self.connection = psycopg.connect(
            dbname="postgres", user="postgres", password="password", host="127.0.0.1", port="5432"
        )
        self.cursor = self.connection.cursor()

    def my_table(self):
        query = """
            CREATE TABLE IF NOT EXISTS my_file( 
                id SERIAL PRIMARY KEY,
                Rank_num INT,
                Peak INT,
                All_peak INT,
                Act_gross BIGINT,
                Adj_gross BIGINT,
                Artist VARCHAR(150),
                Title_tour VARCHAR(250),
                Title_years VARCHAR(50),
                Shows INT,
                Av_gross BIGINT
            );
        """
        self.cursor.execute(query)

    def save_file(self, s_file):
        query = """
            INSERT INTO my_file (Rank_num, Peak, All_peak, Act_gross, Adj_gross, Artist, Title_tour, Title_years, Shows, Av_gross)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        self.cursor.execute(query, s_file)

    def close_file(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        print("\n--- ООП-УПРАВЛЕНЕЦ БАЗЫ: ВСЕ ЗАПИСАНО И ЗАКРЫТО! ---")


# =====================================================================
# ШАГ 4: ФУНКЦИЯ-ФИЛЬТР ТРАНСПОРТЁРНОЙ ЛЕНТЫ
# =====================================================================
def cleen_file():
    new_file = []
    for f in file_rows:
        # ИСПРАВЛЕНО: Распаковываем строго по карте, полученной из экспертизы!
        rank, peak, all_peak, act_gross, adj_gross, artist, title_tour, title_years, shows, av_gross = f

        # Штампуем робота-очистителя
        clean_new_file = MarketFilter(rank, peak, all_peak, act_gross, adj_gross, artist, title_tour, title_years,
                                      shows, av_gross)
        new_clean_file = clean_new_file.ret_filter()
        new_file.append(new_clean_file)
    return new_file


# =====================================================================
# 🎮 ГЛАВНЫЙ ЗАПУСКНОЙ ПУЛЬТ УПРАВЛЕНИЯ
# =====================================================================
file_data = cleen_file()
ft = Connect()
ft.my_table()

print(f"🚀 Начинаем запись {len(file_data)} строк мирового Kaggle-датасета в PostgreSQL...")
for row in file_data:
    ft.save_file(row)

ft.close_file()
