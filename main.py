import itertools
import re
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

@dataclass
class CharacterStats:
    """Класс для хранения характеристик персонажа"""
    strength: int = 0
    dexterity: int = 0
    intelligence: int = 0
    health: int = 0
    energy_shield: int = 0
    mana: int = 0
    spirit: int = 0
    armor: int = 0
    evasion: int = 0
    block: int = 0
    fire_resistance: int = 0
    lightning_resistance: int = 0
    cold_resistance: int = 0
    chaos_resistance: int = 0
    accuracy: int = 0
    physical_damage_min: int = 0
    physical_damage_max: int = 0
    fire_damage_min: int = 0
    fire_damage_max: int = 0
    health_regen: float = 0
    life_leech_percent: float = 0
    mana_leech_percent: float = 0
    mana_regen_percent: float = 0
    item_rarity_percent: float = 0
    evasion_percent: float = 0
    
    def add_stats(self, other):
        """Сложение характеристик"""
        result = CharacterStats()
        for attr in self.__annotations__:
            setattr(result, attr, getattr(self, attr) + getattr(other, attr))
        return result
    
    def __str__(self):
        """Строковое представление характеристик"""
        result = []
        for attr in self.__annotations__:
            value = getattr(self, attr)
            if value != 0:  # Показываем только ненулевые характеристики
                # Преобразуем snake_case в читаемый формат
                attr_name = attr.replace('_', ' ').capitalize()
                result.append(f"{attr_name}: {value}")
        return "\n".join(result)

@dataclass
class JewelryItem:
    """Класс для предметов бижутерии"""
    name: str
    item_type: str  # "ring" или "amulet"
    rarity: str
    level: int
    required_level: int
    stats: CharacterStats
    implicit_stats: CharacterStats = field(default_factory=CharacterStats)
    
    def __str__(self):
        result = [f"{self.name} ({self.item_type})"]
        result.append(f"Редкость: {self.rarity}")
        result.append(f"Уровень предмета: {self.level}")
        result.append(f"Требуется уровень: {self.required_level}")
        
        # Выводим implicit модификаторы
        implicit_str = str(self.implicit_stats)
        if implicit_str:
            result.append("\nImplicit модификаторы:")
            result.append(implicit_str)
        
        # Выводим обычные модификаторы
        result.append("\nМодификаторы:")
        result.append(str(self.stats))
        
        return "\n".join(result)

def parse_jewelry_file(filename: str) -> List[JewelryItem]:
    """Парсинг файла с бижутерией"""
    jewelry_items = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Разделяем на блоки по пустой строке
            item_blocks = content.split('\n\n')
            
            for block in item_blocks:
                if not block.strip():
                    continue
                
                lines = block.strip().split('\n')
                
                # Парсим основную информацию
                item_class = None
                rarity = None
                name = None
                item_type = None
                required_level = 0
                item_level = 0
                
                # Флаги для определения секций
                in_implicit = False
                in_stats = False
                
                # Статы
                stats = CharacterStats()
                implicit_stats = CharacterStats()
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    
                    if not line or line == '--------':
                        continue
                    
                    # Парсим класс предмета
                    if line.startswith('Класс предмета:'):
                        item_class = line.split(':', 1)[1].strip()
                        if 'Кольца' in item_class:
                            item_type = 'ring'
                        elif 'Амулеты' in item_class:
                            item_type = 'amulet'
                    
                    # Парсим редкость
                    elif line.startswith('Редкость:'):
                        rarity = line.split(':', 1)[1].strip()
                    
                    # Парсим название и тип
                    elif i > 0 and lines[i-1].strip() == 'Редкость: Редкий':
                        parts = line.split()
                        if len(parts) >= 3:
                            name = ' '.join(parts[:-2])
                            item_subtype = ' '.join(parts[-2:])
                    
                    # Парсим требуемый уровень
                    elif line.startswith('Требуется: Уровень'):
                        required_level = int(line.split()[-1])
                    
                    # Парсим уровень предмета
                    elif line.startswith('Уровень предмета:'):
                        item_level = int(line.split(':', 1)[1].strip())
                    
                    # Определяем начало implicit модификаторов
                    elif '(implicit)' in line:
                        in_implicit = True
                        in_stats = False
                        parse_stat_line(line, implicit_stats)
                    
                    # Определяем начало обычных модификаторов
                    elif in_implicit and not in_stats and line and line != '--------':
                        in_implicit = False
                        in_stats = True
                        parse_stat_line(line, stats)
                    
                    # Парсим обычные модификаторы
                    elif in_stats and line and line != '--------':
                        parse_stat_line(line, stats)
                
                # Создаем объект предмета
                if item_type and name:
                    jewelry_items.append(JewelryItem(
                        name=name,
                        item_type=item_type,
                        rarity=rarity,
                        level=item_level,
                        required_level=required_level,
                        stats=stats,
                        implicit_stats=implicit_stats
                    ))
    
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
    
    return jewelry_items

def parse_stat_line(line: str, stats: CharacterStats):
    """Парсит строку с характеристикой и добавляет её в объект stats"""
    # Удаляем "(implicit)" если есть
    line = line.replace('(implicit)', '').strip()
    
    # Парсим характеристики
    
    # Сопротивления
    if '+' in line and 'к сопротивлению' in line:
        value = int(re.search(r'\+(\d+)%', line).group(1))
        if 'огню' in line:
            stats.fire_resistance += value
        elif 'молнии' in line:
            stats.lightning_resistance += value
        elif 'холоду' in line:
            stats.cold_resistance += value
        elif 'хаосу' in line:
            stats.chaos_resistance += value
    
    # Характеристики
    elif 'ко всем характеристикам' in line:
        match = re.search(r'\+(\d+)', line)
        if match:
            value = int(match.group(1))
            stats.strength += value
            stats.dexterity += value
            stats.intelligence += value
    
    # Сила
    elif 'к силе' in line:
        match = re.search(r'\+(\d+)', line)
        if match:
            stats.strength += int(match.group(1))
    
    # Ловкость
    elif 'к ловкости' in line:
        match = re.search(r'\+(\d+)', line)
        if match:
            stats.dexterity += int(match.group(1))
    
    # Интеллект
    elif 'к интеллекту' in line:
        match = re.search(r'\+(\d+)', line)
        if match:
            stats.intelligence += int(match.group(1))
    
    # Здоровье
    elif 'к максимуму здоровья' in line:
        match = re.search(r'\+(\d+)', line)
        if match:
            stats.health += int(match.group(1))
    
    # Мана
    elif 'к максимуму маны' in line:
        match = re.search(r'\+(\d+)', line)
        if match:
            stats.mana += int(match.group(1))
    
    # Меткость
    elif 'к меткости' in line:
        match = re.search(r'\+(\d+)', line)
        if match:
            stats.accuracy += int(match.group(1))
    
    # Уклонение
    elif 'увеличение уклонения' in line:
        match = re.search(r'(\d+)%', line)
        if match:
            stats.evasion_percent += int(match.group(1))
    
    # Редкость предметов
    elif 'повышение редкости найденных предметов' in line:
        match = re.search(r'(\d+)%', line)
        if match:
            stats.item_rarity_percent += int(match.group(1))
    
    # Регенерация здоровья
    elif 'Регенерация' in line and 'здоровья в секунду' in line:
        match = re.search(r'Регенерация (\d+\.?\d*)', line)
        if match:
            stats.health_regen += float(match.group(1))
    
    # Скорость регенерации маны
    elif 'повышение скорости регенерации маны' in line:
        match = re.search(r'(\d+)%', line)
        if match:
            stats.mana_regen_percent += int(match.group(1))
    
    # Физический урон к атакам
    elif 'Добавляет от' in line and 'физического урона к атакам' in line:
        match = re.search(r'от (\d+) до (\d+)', line)
        if match:
            stats.physical_damage_min += int(match.group(1))
            stats.physical_damage_max += int(match.group(2))
    
    # Урон от огня к атакам
    elif 'Добавляет от' in line and 'урона от огня к атакам' in line:
        match = re.search(r'от (\d+) до (\d+)', line)
        if match:
            stats.fire_damage_min += int(match.group(1))
            stats.fire_damage_max += int(match.group(2))
    
    # Похищение здоровья
    elif 'физического урона от атак похищается в виде здоровья' in line:
        match = re.search(r'(\d+\.?\d*)%', line)
        if match:
            stats.life_leech_percent += float(match.group(1))
    
    # Похищение маны
    elif 'физического урона от атак похищается в виде маны' in line:
        match = re.search(r'(\d+\.?\d*)%', line)
        if match:
            stats.mana_leech_percent += float(match.group(1))

def find_optimal_combination(jewelry_items: List[JewelryItem]) -> Tuple[List[JewelryItem], CharacterStats]:
    """Находит оптимальную комбинацию колец и амулета"""
    rings = [item for item in jewelry_items if item.item_type == 'ring']
    amulets = [item for item in jewelry_items if item.item_type == 'amulet']
    
    if len(rings) < 2:
        print("Недостаточно колец для выбора (нужно минимум 2).")
        return [], CharacterStats()
    
    if not amulets:
        print("Нет доступных амулетов.")
        return [], CharacterStats()
    
    best_combination = None
    best_stats = None
    best_score = float('-inf')
    
    # Перебираем все возможные комбинации
    for ring_pair in itertools.combinations(rings, 2):
        for amulet in amulets:
            # Суммируем характеристики
            combined_stats = CharacterStats()
            
            # Добавляем характеристики от предметов (включая implicit)
            for item in [ring_pair[0], ring_pair[1], amulet]:
                combined_stats = combined_stats.add_stats(item.stats)
                combined_stats = combined_stats.add_stats(item.implicit_stats)
            
            # Вычисляем общий "счет" для этой комбинации
            score = calculate_score(combined_stats)
            
            if score > best_score:
                best_score = score
                best_combination = [ring_pair[0], ring_pair[1], amulet]
                best_stats = combined_stats
    
    return best_combination, best_stats

def calculate_score(stats: CharacterStats) -> float:
    """
    Вычисляет общий "счет" для набора характеристик.
    Можно настроить веса для разных характеристик в зависимости от билда.
    """
    # Пример весов для разных характеристик
    weights = {
        'strength': 1.0,
        'dexterity': 3.0,
        'intelligence': 1.0,
        'health': 2.0,
        'energy_shield': 1.0,
        'mana': 1.0,
        'spirit': 2.0,
        'armor': 0.5,
        'evasion': 2.0,
        'block': 1.0,
        'fire_resistance': 5.0,
        'lightning_resistance': 5.0,
        'cold_resistance': 5.0,
        'chaos_resistance': 5.0,
        'accuracy': 1.0,
        'physical_damage_min': 1.0,
        'physical_damage_max': 1.0,
        'fire_damage_min': 1.0,
        'fire_damage_max': 1.0,
        'health_regen': 1.0,
        'life_leech_percent': 1.0,
        'mana_leech_percent': 1.0,
        'mana_regen_percent': 1.0,
        'item_rarity_percent': 1.0,
        'evasion_percent': 1.0
    }
    
    score = 0
    for attr, weight in weights.items():
        score += getattr(stats, attr) * weight
    
    return score

def main():
    print("Калькулятор оптимизации характеристик для Path of Exile 2")
    print("=" * 60)
    
    filename = "1.txt"
    print(f"Чтение данных из файла {filename}...")
    jewelry_items = parse_jewelry_file(filename)
    
    if not jewelry_items:
        print("Не удалось загрузить предметы бижутерии.")
        return
    
    print(f"Загружено {len(jewelry_items)} предметов:")
    rings = [item for item in jewelry_items if item.item_type == 'ring']
    amulets = [item for item in jewelry_items if item.item_type == 'amulet']
    print(f"- Кольца: {len(rings)}")
    print(f"- Амулеты: {len(amulets)}")
    print()
    
    # Удаляем вывод загруженных предметов
    # print("Загруженные предметы:")
    # print("=" * 60)
    # for item in jewelry_items:
    #     print(f"{item}\n")
    
    best_combination, best_stats = find_optimal_combination(jewelry_items)
    
    if best_combination:
        print("Оптимальная комбинация:")
        print("=" * 60)
        for item in best_combination:
            print(f"{item.item_type.capitalize()}: {item.name}")
        
        print("\nИтоговые характеристики:")
        print("=" * 60)
        print(best_stats)
    else:
        print("Не удалось найти оптимальную комбинацию.")

if __name__ == "__main__":
    main()