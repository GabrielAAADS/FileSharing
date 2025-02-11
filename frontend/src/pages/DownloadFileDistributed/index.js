import { useState } from 'react';
import './styles.css';
import axios from 'axios';

function DownloadFileDistributed() {
  const [clientPort, setClientPort] = useState("0");
  const [client1, setClient1] = useState(false);
  const [client2, setClient2] = useState(false);
  const [client3, setClient3] = useState(false);
  const [filename, setFilename] = useState("");
  const [filesize, setFilesize] = useState("");

  const handleSearch = async() => {
    if(clientPort === "0") {
      alert("Selecione o cliente que irá fazer o download!");
      return;
    }

    let sources = [];
    if(client1) {
      sources.push({
        ip: "127.0.0.1",
        port: 1235,
      });
    }
    if(client2) {
      sources.push({
        ip: "127.0.0.1",
        port: 1236,
      });
    }
    if(client3) {
      sources.push({
        ip: "127.0.0.1",
        port: 1237,
      });
    }

    console.log(clientPort, {
      filename,
      filesize,
      sources
    });
    await axios.post(`http://localhost:${clientPort}/download/distributed`, {
      filename,
      filesize: parseInt(filesize),
      sources,
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    }).then(v => {
      alert("Arquivo baixado com sucesso!");
      setClientPort("0");
      setFilename("");
      setFilesize("");
      setClient1(false);
      setClient2(false);
      setClient3(false);
    })
    .catch(err => {
      console.log("ERROR", err.response);
      alert(err.response.data?.detail ?? "Ocorreu um erro ao tentar baixar o arquivo de maneira distribuida")
    });
  };

  return (
    <div className="container">
      <div className="subcontainer">
        <h1>Baixar Arquivos</h1>
        
        <p>Selecione pra qual cliente você deseja que o download seja feito</p>
        <select value={clientPort} onChange={v => setClientPort(v.target.value)}>
          <option value="0">Selecione o cliente</option>
          <option value="8000">Cliente 1</option>
          <option value="8001">Cliente 2</option>
          <option value="8002">Cliente 3</option>
        </select>
        
        <p>Digite o nome do arquivo</p>
        <input placeholder="Digite o nome do arquivo" value={filename} onChange={ev => setFilename(ev.target.value)} />
        <p>Digite o quanto em memória você quer baixar do arquivo</p>
        <input value={filesize} onChange={ev => setFilesize(ev.target.value)} />

        <p>Selecione de quais clientes você quer baixar esse arquivo</p>
        <div>
          <input
            onClick={() => setClient1(!client1)}
            type="checkbox"
            style={{marginBottom: 0}}
            checked={client1}
            onChange={ev => setClient1(!client1)}
          />
          <p>Cliente 1</p>
        </div>

        <div>
          <input
            onClick={() => setClient2(!client2)}
            type="checkbox"
            style={{marginBottom: 0}}
            checked={client2}
            onChange={ev => setClient2(!client2)}
          />
          <p>Cliente 2</p>
        </div>

        <div>
          <input
            onClick={() => setClient3(!client3)}
            type="checkbox"
            style={{marginBottom: 0}}
            checked={client3}
            onChange={ev => setClient3(!client3)}
          />
          <p>Cliente 3</p>
        </div>

        <button onClick={() => handleSearch()}>Baixar</button>
      </div>
    </div>
  );
}

export default DownloadFileDistributed;
