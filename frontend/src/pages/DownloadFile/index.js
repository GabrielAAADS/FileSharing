import { useState } from 'react';
import './styles.css';
import axios from 'axios';

function DownloadFile() {
  const [client1Port, setClient1Port] = useState("0");
  const [client2Port, setClient2Port] = useState("0");
  const [filename, setFilename] = useState("");
  const [offsetStart, setOffsetStart] = useState("");
  const [offsetEnd, setOffsetEnd] = useState("");

  const handleSearch = async() => {
    if(client1Port === "0" || client2Port === "0") {
      alert("Selecione os clientes!");
      return;
    }
    console.log(client1Port, {
      server_ip: "127.0.0.1",
      port: client2Port,
      filename,
      offset_start: parseInt(offsetStart),
      offset_end: parseInt(offsetEnd),
    });
    await axios.post(`http://localhost:${client1Port}/download`, {
      ip: "127.0.0.1",
      port: client2Port,
      filename,
      offset_start: parseInt(offsetStart),
      offset_end: parseInt(offsetEnd),
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    }).then(v => {
      alert("Arquivo baixado com sucesso!");
      setClient1Port("0");
      setClient2Port("0");
      setFilename("");
      setOffsetStart("");
      setOffsetEnd("");
    })
    .catch(err => {
      console.log("ERROR", err.response);
      alert(err.response.data?.detail ?? "Ocorreu um erro ao tentar baixar o arquivo")
    });
  };

  return (
    <div className="container">
      <div className="subcontainer">    
        <h1>Baixar Arquivos</h1>
        
        <p>Selecione pra qual cliente você deseja que o download seja feito</p>
        <select value={client1Port} onChange={v => setClient1Port(v.target.value)}>
          <option value="0">Selecione o cliente</option>
          <option value="8000">Cliente 1</option>
          <option value="8001">Cliente 2</option>
          <option value="8002">Cliente 3</option>
        </select>
        
        <p>Selecione de que cliente você deseja fazer o download</p>
        <select value={client2Port} onChange={v => setClient2Port(v.target.value)}>
          <option value="0">Selecione o cliente</option>
          <option value="1235">Cliente 1</option>
          <option value="1236">Cliente 2</option>
          <option value="1237">Cliente 3</option>
        </select>

        <p>Digite o nome do arquivo</p>
        <input placeholder="Digite o nome do arquivo" value={filename} onChange={ev => setFilename(ev.target.value)} />
        <p>Offset Start</p>
        <input placeholder="Digite o offset start do arquivo" value={offsetStart} onChange={ev => setOffsetStart(ev.target.value)} />
        <p>Offset End</p>
        <input placeholder="Digite o offset end do arquivo" value={offsetEnd} onChange={ev => setOffsetEnd(ev.target.value)} />

        <button onClick={() => handleSearch()}>Baixar</button>
      </div>
    </div>
  );
}

export default DownloadFile;
