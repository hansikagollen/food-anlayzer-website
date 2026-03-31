import axios from "axios";

const API_URL = "http://127.0.0.1:8000/predict";

function Upload({ setResult, updateHistory }) {

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const res = await axios.post(API_URL, formData);

    setResult(res.data);
    updateHistory(res.data);
  };

  return (
    <div className="card">
      <h3>📤 Upload Image</h3>
      <input type="file" onChange={handleUpload} />
    </div>
  );
}

export default Upload;