import axios from 'axios';
import './styles.css';
import { useState } from 'react';

function DisconnectServer() {
  const [id, setId] = useState(-1);
  const publicFolders = ["C:\\public", "C:\\public2", "C:\\public3"];

  const handleDisconnect = async() => {
    if(id === -1) {
      alert("Selecione um cliente!");
      return;
    }
    await axios.post(`http://localhost:${8000 + id}/leave`, {
      server_ip: "127.0.0.1",
      client_port: `${1235 + id}`,
      public_folder: publicFolders[id]
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    }).then(v => {
      alert("Cliente desconectado com sucesso");
      setId(-1);
    })
    .catch(err => {
      console.log("ERROR");
      alert(err.response.data?.detail ?? "Ocorreu um erro ao tentar desconectar o cliente")
    });
  };

  return (
    <div className="container">
      <h1>Desconectar cliente do servidor</h1>
      <p>Selecione qual cliente deseja desconectar</p>
      <select value={id+1} onChange={v => setId(v.target.value - 1)}>
        <option value={0}>Selecione o cliente</option>
        <option value={1}>Cliente 1</option>
        <option value={2}>Cliente 2</option>
        <option value={3}>Cliente 3</option>
      </select>
      <button onClick={() => handleDisconnect()}>Desconectar</button>
    </div>
  );
}

export default DisconnectServer;
