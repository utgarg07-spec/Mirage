import { BrowserRouter, Route, Routes } from "react-router-dom";
import NodeOne from "./pages/NodeOne";
import NodeTwo from "./pages/NodeTwo";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<NodeOne />} />
        <Route path="/node2" element={<NodeTwo />} />
      </Routes>
    </BrowserRouter>
  );
}
