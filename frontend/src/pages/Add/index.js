import { useState } from 'react';
import './styles.css';
import axios from 'axios';

function Add() {
  const [id, setId] = useState(-1);

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);

    if (selectedFile) {
      setPreview(URL.createObjectURL(selectedFile)); // Cria uma URL para pré-visualização
    }
  };

  const handleConnect = async() => {
    if(id === -1 || !file) {
      alert("Selecione um cliente!");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    console.log(`http://localhost:${8000 + id}/upload`);
    await axios.post(`http://localhost:${8000 + id}/upload`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then(v => {
      alert("Arquivo adicionado com sucesso!");
      setId(-1);
      setFile(null);
      setPreview(null);
    })
    .catch(err => {
      console.log("ERROR");
      alert(err.response?.data?.detail ?? "Ocorreu um erro ao tentar adicionar o arquivo")
    });
  };

  return (
    <div className="container">
      <div className="subcontainer">
        <h1>Conectar cliente ao servidor</h1>
        <p>Selecione qual cliente deseja conectar</p>
        <select value={id+1} onChange={v => setId(v.target.value - 1)}>
          <option value={0}>Selecione o cliente</option>
          <option value={1}>Cliente 1</option>
          <option value={2}>Cliente 2</option>
          <option value={3}>Cliente 3</option>
        </select>
        <p>Selecione o arquivo que deseja adicionar à pasta do cliente</p>
        <input type="file" accept="image/*" onChange={handleFileChange} />
        {preview && <img src={preview} alt="Preview" width="100px" />}
        <button onClick={() => handleConnect()}>Adicionar</button>
      </div>
    </div>
  );
}

export default Add;
