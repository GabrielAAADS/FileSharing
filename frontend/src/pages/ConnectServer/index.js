import { useState } from 'react';
import './styles.css';
import axios from 'axios';

function ConnectServer() {
  const [id, setId] = useState(-1);
  const publicFolders = ["C:\\public", "C:\\public2", "C:\\public3"];

  const handleConnect = async() => {
    if(id === -1) {
      alert("Selecione um cliente!");
      return;
    }
    console.log(`http://localhost:${8000 + id}/connect`);
    await axios.post(`http://localhost:${8000 + id}/connect`, {
      server_ip: "127.0.0.1",
      client_ip: "localhost",
      client_port: `${1235 + id}`,
      public_folder: publicFolders[id]
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    }).then(v => {
      alert("Conexão estabelecida com sucesso");
      setId(-1);
    })
    .catch(err => {
      console.log("ERROR");
      alert(err.response?.data?.detail ?? "Ocorreu um erro ao tentar estabelecer a conexão")
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
        <button onClick={() => handleConnect()}>Conectar</button>
      </div>
    </div>
  );
}

export default ConnectServer;
