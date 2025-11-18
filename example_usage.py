"""Пример программного использования BlinkDetector."""

import cv2
import time
from blink_checker.detector import BlinkDetector


def simple_example():
    """Простой пример использования детектора моргания."""
    print("🚀 Пример использования BlinkDetector\n")
    
    # Инициализация детектора без alarm
    detector = BlinkDetector(alarm_threshold=0)
    print("✅ Детектор инициализирован")
    
    # Открытие камеры
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Не удалось открыть камеру")
        return
    
    print("✅ Камера открыта")
    print("⏳ Мониторинг в течение 10 секунд...\n")
    
    start_time = time.time()
    duration = 10  # секунд
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Обнаружение моргания
        blink_detected, ear, annotated_frame = detector.detect_blink(frame)
        
        if blink_detected:
            print(f"👁️ Моргание! Всего: {detector.get_blink_count()}, EAR: {ear:.3f}")
        
        # Отображение кадра (опционально)
        cv2.imshow("Example", annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Завершение
    cap.release()
    cv2.destroyAllWindows()
    
    # Результаты
    total_time = time.time() - start_time
    blinks = detector.get_blink_count()
    bpm = (blinks / total_time) * 60 if total_time > 0 else 0
    
    print(f"\n📊 Результаты:")
    print(f"   Время: {total_time:.1f}с")
    print(f"   Морганий: {blinks}")
    print(f"   Частота: {bpm:.1f} раз/мин")


def custom_parameters_example():
    """Пример с настройкой параметров детектора."""
    print("\n" + "="*60)
    print("🔧 Пример с кастомными параметрами\n")
    
    # Создание детектора
    detector = BlinkDetector()
    
    # Настройка параметров
    detector.EAR_THRESHOLD = 0.25  # Более высокий порог
    detector.CONSECUTIVE_FRAMES = 3  # Больше кадров для подтверждения
    
    print(f"⚙️ Порог EAR: {detector.EAR_THRESHOLD}")
    print(f"⚙️ Кадров для подтверждения: {detector.CONSECUTIVE_FRAMES}")
    print("\nЭти параметры сделают детекцию более строгой")
    
    # ... остальной код аналогично simple_example()


def alarm_example():
    """Пример использования с функцией alarm."""
    print("\n" + "="*60)
    print("🚨 Пример с функцией alarm\n")
    
    # Инициализация детектора с alarm через 8 секунд
    detector = BlinkDetector(alarm_threshold=8)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Не удалось открыть камеру")
        return
    
    print("⏰ Сигнал сработает, если не моргнете 8 секунд")
    print("👁️ Попробуйте не моргать, чтобы услышать сигнал!\n")
    
    start_time = time.time()
    duration = 15
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            break
        
        blink_detected, ear, annotated_frame = detector.detect_blink(frame)
        
        if blink_detected:
            print(f"👁️ Моргание! Всего: {detector.get_blink_count()}")
        
        # Проверка alarm
        if detector.should_alarm():
            print("🚨 ALARM! Пожалуйста, моргните! 🚨")
            print('\a')  # System beep
        
        # Показать время с последнего моргания
        time_since = detector.get_time_since_last_blink()
        if time_since > 5:
            print(f"⚠️ {time_since:.1f}s без моргания...")
        
        cv2.imshow("Alarm Example", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n✅ Завершено. Всего морганий: {detector.get_blink_count()}")


def headless_example():
    """Пример работы без GUI (только консольный вывод)."""
    print("\n" + "="*60)
    print("💻 Пример работы без GUI (headless mode)\n")
    
    detector = BlinkDetector(alarm_threshold=0)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Не удалось открыть камеру")
        return
    
    start_time = time.time()
    duration = 5
    
    print(f"⏱️ Мониторинг {duration} секунд без отображения видео...\n")
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Обнаружение без отображения
        blink_detected, ear, _ = detector.detect_blink(frame)
        
        if blink_detected:
            elapsed = time.time() - start_time
            print(f"[{elapsed:05.2f}s] Моргание #{detector.get_blink_count()}, EAR: {ear:.3f}")
    
    cap.release()
    
    print(f"\n✅ Завершено. Всего морганий: {detector.get_blink_count()}")


if __name__ == "__main__":
    print("="*60)
    print("👁️ Примеры использования AI Eye Blink Checker")
    print("="*60)
    
    # Запуск примеров
    try:
        # simple_example()
        alarm_example()  # Раскомментируйте для запуска
        # custom_parameters_example()  # Раскомментируйте для запуска
        # headless_example()  # Раскомментируйте для запуска
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    
    print("\n" + "="*60)
    print("✅ Примеры завершены!")
    print("="*60)

