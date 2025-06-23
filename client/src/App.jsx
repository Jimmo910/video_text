import { useState, useRef } from "react";
import axios from "axios";

export default function App() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [model, setModel] = useState("base");
  const [splitText, setSplitText] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [elapsed, setElapsed] = useState(0); // прошедшее время в секундах
  const [predicted, setPredicted] = useState(null); // предполагаемое время
  const timerRef = useRef(null); // ссылка на интервал

  const handleFileChange = (e) => {
    if (!loading) setFile(e.target.files[0]); // Блокируем выбор файла во время обработки
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || loading) return; // Блокируем повторное нажатие

    setLoading(true);
    setError(null);
    setText("");
    setElapsed(0); // обнуляем таймер
    setPredicted(null);

    // запрашиваем примерное время
    const ext = file.name.split('.').pop().toLowerCase();
    try {
      const estimateData = new FormData();
      estimateData.append('file_size', file.size);
      estimateData.append('extension', ext);
      estimateData.append('model', model);
      const estRes = await axios.post(
        import.meta.env.VITE_API_URL + '/estimate',
        estimateData,
      );
      setPredicted(estRes.data.estimated_time);
    } catch (err) {
      console.error('Ошибка оценки времени:', err);
    }
    // запускаем счетчик секунд
    timerRef.current = setInterval(() => {
      setElapsed((prev) => prev + 1);
    }, 1000);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("model", model);
    formData.append("split", splitText);

    try {
      const response = await axios.post(import.meta.env.VITE_API_URL + "/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      console.log("Ответ сервера:", response);
      setText(response.data.text);
    } catch (err) {
      console.error("Ошибка:", err);
      setError("Ошибка загрузки файла");
    }
    setLoading(false);
    clearInterval(timerRef.current); // останавливаем таймер

    if (soundEnabled) {
      const audio = new Audio("/done.mp3");
      audio.play().catch((err) => console.error("Ошибка воспроизведения звука:", err));
    }

  };

  const copyToClipboard = () => {
    if (text) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text)
          .then(() => alert("Текст скопирован!"))
          .catch((err) => {
            console.error("Ошибка копирования:", err);
            fallbackCopyText(text);
          });
      } else {
        fallbackCopyText(text);
      }
    }
  };

  const fallbackCopyText = (text) => {
    try {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.setAttribute("readonly", "");
      textarea.style.position = "absolute";
      textarea.style.left = "-9999px";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      alert("Текст скопирован!");
    } catch (err) {
      console.error("Не удалось скопировать текст:", err);
      alert("Ошибка копирования");
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-6">
      <h1 className="text-2xl font-bold mb-4">Загрузка видео</h1>
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md w-full max-w-md">
        <input
          type="file"
          accept=".mp4,.mov,.avi,.mkv,.webm,.flv,.wmv,.m4v"
          onChange={handleFileChange}
          className="w-full mb-4"
          disabled={loading} // Блокируем выбор файла
        />
        <label className="block mb-2 font-medium">Выберите модель:</label>
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="w-full mb-4 p-2 border rounded-md"
          disabled={loading} // Блокируем выбор модели
        >
          <option value="small">Small (медленнее, точнее)</option>
          <option value="medium">Medium (медленно, более точно)</option>
          <option value="large">Large (самая точная, но медленная)</option>
        </select>
        <label className="inline-flex items-center mb-4">
          <input
            type="checkbox"
            checked={soundEnabled}
            onChange={() => setSoundEnabled(!soundEnabled)}
            className="mr-2"
          />
          Звуковое оповещение
        </label>

        <button
          type="submit"
          className="w-full bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
          disabled={loading} // Блокируем кнопку
        >
          {loading ? "Обработка..." : "Загрузить"}
        </button>
      </form>

      {loading && (
        predicted !== null ? (
          <p className="mt-4">Примерно осталось: {Math.round(predicted - elapsed)} c</p>
        ) : (
          <p className="mt-4">Время обработки: {elapsed} c</p>
        )
      )}

      {error && <p className="text-red-500 mt-4">{error}</p>}

      {text && (
        <div className="mt-4 p-4 bg-white rounded-lg shadow-md w-full max-w-md">
          <h2 className="font-bold mb-2">Распознанный текст:</h2>
          <button
            onClick={copyToClipboard}
            className="mt-3 w-full bg-green-500 text-white p-2 rounded-md hover:bg-green-600"
          >
            Копировать
          </button>
          <p className="whitespace-pre-wrap">{text}</p>
        </div>
      )}
    </div>
  );
}