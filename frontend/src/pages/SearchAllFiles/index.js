import axios from 'axios';
import { useState } from 'react';
import './styles.css';

function SearchAllFiles() {
  const [data, setData] = useState([]);
  const [id, setId] = useState(-1);

  const handleSearch = async() => {
    if(id === -1) {
      alert("Selecione um cliente!");
      return;
    }
    await axios.get(`http://localhost:${8000 + id}/search`, {
      headers: {
        'Content-Type': 'application/json'
      }
    }).then(v => {
      alert("Arquivos buscados com sucesso");
      setData(v.data.results);
    })
    .catch(err => {
      console.log("ERROR");
      alert(err.response.data?.detail ?? "Ocorreu um erro ao tentar buscar os arquivos")
    });
  };

  return (
    <div className="container">
      <div className="subcontainer">
        <h1>Todos os Arquivos</h1>
        <p>Selecione um cliente</p>
        <select value={id+1} onChange={v => setId(v.target.value - 1)}>
          <option value={0}>Selecione o cliente</option>
          <option value={1}>Cliente 1</option>
          <option value={2}>Cliente 2</option>
          <option value={3}>Cliente 3</option>
        </select>
        <button onClick={() => handleSearch()}>Buscar</button>
        <div style={{flexDirection: "column"}}>
          {data.map(v => {
            return (
              <div className="card">
                <p>Nome do arquivo: {v.filename}</p>
                <p>Porta do cliente portador: {v.port}</p>
                <p>Tamanho do arquivo: {v.size}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default SearchAllFiles;
