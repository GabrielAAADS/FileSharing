import "./styles.css";
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div className="subcontainer" style={{margin: 30}}>
      <h1>Home</h1>
      <Link className="card-home" to="/connect">Conectar com o servidor</Link>
      <Link className="card-home" to="/disconnect">Desconectar com o servidor</Link>
      <Link className="card-home" to="/add">Adicionar um arquivo à pasta de algum cliente</Link>
      <Link className="card-home" to="/download">Fazer download de um arquivo</Link>
      <Link className="card-home" to="/downloadDistributed">Fazer download de um arquivo de maneira distribuída</Link>
      <Link className="card-home" to="/searchall">Ver todos os arquivos</Link>
      <Link className="card-home" to="/search">Procurar arquivos</Link>
      <Link className="card-home" to="/searchbypattern">Procurar arquivos por pattern</Link>
    </div>
  );
}

export default Home;
