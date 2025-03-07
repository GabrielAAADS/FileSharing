import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './App.css';
import ConnectServer from './pages/ConnectServer';
import DisconnectServer from './pages/DisconnectServer';
import DownloadFile from './pages/DownloadFile';
import SearchAllFiles from './pages/SearchAllFiles';
import SearchFiles from './pages/SearchFiles';
import SearchByPattern from './pages/SearchByPattern';
import Home from './pages/Home';
import DownloadFileDistributed from './pages/DownloadFileDistributed';
import Add from './pages/Add';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route index element={<Home />} />
        <Route path="connect" element={<ConnectServer />} />
        <Route path="disconnect" element={<DisconnectServer />} />
        <Route path="add" element={<Add />} />
        <Route path="download" element={<DownloadFile />} />
        <Route path="downloadDistributed" element={<DownloadFileDistributed />} />
        <Route path="searchall" element={<SearchAllFiles />} />
        <Route path="search" element={<SearchFiles />} />
        <Route path="searchbypattern" element={<SearchByPattern />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
