import "./styles.css";
import { Link } from 'react-router-dom';

function Home() {
  const handleSearch = () => {

  };

  return (
    <div className="container">
      <h1>Home</h1>
      <Link to="/connect">Conectar com o servidor</Link>
      <Link to="/disconnect">Desconectar com o servidor</Link>
      <Link to="/download">Fazer download de um arquivo</Link>
      <Link to="/downloadDistributed">Fazer download de um arquivo de maneira distribuída</Link>
      <Link to="/searchall">Ver todos os arquivos</Link>
      <Link to="/search">Procurar arquivos</Link>
      <Link to="/searchbypattern">Procurar arquivos por pattern</Link>
    </div>
  );
}

export default Home;
