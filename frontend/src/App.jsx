import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { Gem, Menu, Search, Bell, User, Settings, DollarSign, Package, Users, FileText, LogOut, LayoutDashboard, Diamond, HandCoins, ShoppingBag, FolderOpen, ChevronDown, ChevronUp, Bot } from 'lucide-react'
import { Button } from './components/ui/button.jsx'
import { Input } from './components/ui/input.jsx'
import { Badge } from './components/ui/badge.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs.jsx'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import './App.css'

// Importar novos componentes
import Clientes from './components/Clientes.jsx';
import Funcionarios from './components/Funcionarios.jsx';
import JoiasMaterial from './components/JoiasMaterial.jsx';
import JoiasMateriaisPedrasRel from './components/JoiasMateriaisPedrasRel.jsx';
import JoiasPedras from './components/JoiasPedras.jsx';
import JoiasTamanhos from './components/JoiasTamanhos.jsx';
import Caixa from './components/Caixa.jsx';
import Custos from './components/Custos.jsx';
import Descontos from './components/Descontos.jsx';
import Entradas from './components/Entradas.jsx';
import Impostos from './components/Impostos.jsx';
import Vales from './components/Vales.jsx';
import FolhaPagamento from './components/FolhaPagamento.jsx';
import Pagamentos from './components/Pagamentos.jsx';
import Prazos from './components/Prazos.jsx';
import Encomendas from './components/Encomendas.jsx';
import EncomendasJoias from './components/EncomendasJoias.jsx';
import Estoque from './components/Estoque.jsx';
import EstoqueFiltros from './components/EstoqueFiltros.jsx';
import Cartas from './components/Cartas.jsx';
import Notas from './components/Notas.jsx';
import ErrosAoColar from './components/ErrosAoColar.jsx';
import Joias from './components/Joias.jsx';
import Padroes from './components/Padroes.jsx';
import ErrorBoundary from './components/ErrorBoundary.jsx';
import LoginScreen from './components/LoginScreen.jsx';
import LuaChat from './components/LuaChat.jsx';
import LuaSuperChat from './components/LuaSuperChat.jsx';
import LuaFreeChat from './components/LuaFreeChat.jsx';
import Assistant from './components/Assistant.jsx';
import DashboardEditavel from './components/DashboardEditavel.jsx';

// Importar Contextos e Modais
import { ModalProvider } from './contexts/ModalContext.jsx';
import ValeModal from './components/modals/ValeModal.jsx';
import EncomendasModal from './components/modals/EncomendasModal.jsx';
import InventoryModal from './components/modals/InventoryModal.jsx';
import SalesModal from './components/modals/SalesModal.jsx';
import PdfHistoryModal from './components/modals/PdfHistoryModal.jsx';

// Importar modais da Lua para funcionamento independente do chat
import FuncionariosModal from './components/modals/FuncionariosModal.jsx';
import VendasModal from './components/modals/VendasModal.jsx';
import EncomendasLuaModal from './components/modals/EncomendasLuaModal.jsx';
import ValesLuaModal from './components/modals/ValesLuaModal.jsx';
import EnergiaModal from './components/modals/EnergiaModal.jsx';

// Componente de Layout Principal
function Layout({ children, handleLogout }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [adminMenuOpen, setAdminMenuOpen] = useState(false)
  const [catalogMenuOpen, setCatalogMenuOpen] = useState(false)
  const [financeMenuOpen, setFinanceMenuOpen] = useState(false)
  const [salesStockMenuOpen, setSalesStockMenuOpen] = useState(false)
  const [otherMenuOpen, setOtherMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-black flex flex-col">
      {/* Header */}
      <header className="bg-black shadow-sm border-b border-gray-800 z-10">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden text-white hover:bg-gray-800"
            >
              <Menu className="h-5 w-5" />
            </Button>
            <div className="flex items-center space-x-2">
              <img src="/images/logo.png" alt="Logo Antônio Rabelo" className="h-8 w-8" />
              <h1 className="text-xl font-bold text-white">Antônio Rabelo</h1>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="relative hidden md:block">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Pesquisar..."
                className="pl-10 w-64 bg-gray-800 border-gray-700 text-white placeholder-gray-400"
              />
            </div>
            <Button variant="ghost" size="sm" className="text-white hover:bg-gray-800">
              <Bell className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="sm" className="text-white hover:bg-gray-800">
              <User className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="sm" className="text-white hover:bg-gray-800" onClick={handleLogout}>
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main content area with sidebar */}
      <div className="flex flex-1">
        {/* Sidebar */}
        <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-black shadow-lg transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-200 ease-in-out lg:translate-x-0 lg:static lg:inset-0 lg:flex-shrink-0`}>
          <nav className="mt-8 px-4">
            <div className="space-y-2">

              <Link to="/">
                <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                  <LayoutDashboard className="mr-2 h-4 w-4" /> Dashboard
                </Button>
              </Link>

              <Link to="/dashboard-editavel">
                <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                  <LayoutDashboard className="mr-2 h-4 w-4" /> Dashboard Editável
                </Button>
              </Link>

              <Link to="/assistant">
                <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                  <Bot className="mr-2 h-4 w-4" /> Assistente Lua
                </Button>
              </Link>

              <Link to="/admin">
                <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                  <Settings className="mr-2 h-4 w-4" /> Painel da Lua
                </Button>
              </Link>

              {/* Administração */}
              <div
                className="flex items-center justify-between cursor-pointer pt-4 pb-2 text-xs font-semibold text-gray-400 uppercase hover:text-white"
                onClick={() => setAdminMenuOpen(!adminMenuOpen)}
              >
                Administração {adminMenuOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </div>
              {adminMenuOpen && (
                <div className="space-y-2 pl-4">
                  <Link to="/clientes">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <Users className="mr-2 h-4 w-4" /> Clientes
                    </Button>
                  </Link>
                  <Link to="/funcionarios">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <User className="mr-2 h-4 w-4" /> Funcionários
                    </Button>
                  </Link>
                  <Link to="/padroes">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <Settings className="mr-2 h-4 w-4" /> Padrões
                    </Button>
                  </Link>
                </div>
              )}

              {/* Catálogo */}
              <div
                className="flex items-center justify-between cursor-pointer pt-4 pb-2 text-xs font-semibold text-gray-400 uppercase hover:text-white"
                onClick={() => setCatalogMenuOpen(!catalogMenuOpen)}
              >
                Catálogo {catalogMenuOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </div>
              {catalogMenuOpen && (
                <div className="space-y-2 pl-4">
                  <Link to="/joias">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <Diamond className="mr-2 h-4 w-4" /> Joias
                    </Button>
                  </Link>
                  <Link to="/padroes">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <FolderOpen className="mr-2 h-4 w-4" /> Padrões
                    </Button>
                  </Link>
                  <Link to="/materiais">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <Gem className="mr-2 h-4 w-4" /> Materiais
                    </Button>
                  </Link>
                  <Link to="/pedras">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <Gem className="mr-2 h-4 w-4" /> Pedras
                    </Button>
                  </Link>
                </div>
              )}

              {/* Financeiro */}
              <div
                className="flex items-center justify-between cursor-pointer pt-4 pb-2 text-xs font-semibold text-gray-400 uppercase hover:text-white"
                onClick={() => setFinanceMenuOpen(!financeMenuOpen)}
              >
                Financeiro {financeMenuOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </div>
              {financeMenuOpen && (
                <div className="space-y-2 pl-4">
                  <Link to="/caixa">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <HandCoins className="mr-2 h-4 w-4" /> Caixa
                    </Button>
                  </Link>
                  <Link to="/custos">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <DollarSign className="mr-2 h-4 w-4" /> Custos
                    </Button>
                  </Link>
                  <Link to="/descontos">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <DollarSign className="mr-2 h-4 w-4" /> Descontos
                    </Button>
                  </Link>
                  <Link to="/entradas">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <DollarSign className="mr-2 h-4 w-4" /> Entradas
                    </Button>
                  </Link>
                  <Link to="/impostos">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <DollarSign className="mr-2 h-4 w-4" /> Impostos
                    </Button>
                  </Link>
                  <Link to="/vales">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <DollarSign className="mr-2 h-4 w-4" /> Vales
                    </Button>
                  </Link>
                  <Link to="/folha-pagamento">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <DollarSign className="mr-2 h-4 w-4" /> Folha de Pagamento
                    </Button>
                  </Link>
                  <Link to="/pagamentos">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <DollarSign className="mr-2 h-4 w-4" /> Pagamentos
                    </Button>
                  </Link>
                  <Link to="/prazos">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <DollarSign className="mr-2 h-4 w-4" /> Prazos
                    </Button>
                  </Link>
                </div>
              )}

              {/* Vendas/Estoque */}
              <div
                className="flex items-center justify-between cursor-pointer pt-4 pb-2 text-xs font-semibold text-gray-400 uppercase hover:text-white"
                onClick={() => setSalesStockMenuOpen(!salesStockMenuOpen)}
              >
                Vendas/Estoque {salesStockMenuOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </div>
              {salesStockMenuOpen && (
                <div className="space-y-2 pl-4">
                  <Link to="/encomendas">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <ShoppingBag className="mr-2 h-4 w-4" /> Encomendas
                    </Button>
                  </Link>
                  <Link to="/estoque">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <Package className="mr-2 h-4 w-4" /> Estoque
                    </Button>
                  </Link>
                </div>
              )}

              {/* Outros */}
              <div
                className="flex items-center justify-between cursor-pointer pt-4 pb-2 text-xs font-semibold text-gray-400 uppercase hover:text-white"
                onClick={() => setOtherMenuOpen(!otherMenuOpen)}
              >
                Outros {otherMenuOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </div>
              {otherMenuOpen && (
                <div className="space-y-2 pl-4">
                  <Link to="/cartas">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <FileText className="mr-2 h-4 w-4" /> Cartas
                    </Button>
                  </Link>
                  <Link to="/notas">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <FileText className="mr-2 h-4 w-4" /> Notas
                    </Button>
                  </Link>
                  <Link to="/erros-ao-colar">
                    <Button variant="ghost" className="w-full justify-start text-white hover:bg-gray-800">
                      <FileText className="mr-2 h-4 w-4" /> Erros ao Colar
                    </Button>
                  </Link>
                </div>
              )}
            </div>
          </nav>
        </div>

        {/* Main Content */}
        <main className="flex-1 p-6 lg:ml-64 bg-black text-white">
          {children}
        </main>
      </div>

      {/* Chat da LUA Free Intelligent - sempre visível */}
      <LuaFreeChat />

      {/* Overlay para mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}

// Componente Dashboard
function Dashboard() {
  const [stats, setStats] = useState(null)
  const [jewelryByType, setJewelryByType] = useState([])
  const [materialsByCategory, setMaterialsByCategory] = useState([])
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Buscar estatísticas gerais
        const statsResponse = await fetch('/api/dashboard/overview')
        const statsData = await statsResponse.json()
        setStats(statsData)

        // Buscar joias por tipo
        const jewelryResponse = await fetch('/api/dashboard/jewelry-by-type')
        const jewelryData = await jewelryResponse.json()
        setJewelryByType(jewelryData.data || [])

        // Buscar materiais por categoria
        const materialsResponse = await fetch('/api/dashboard/materials-by-category')
        const materialsData = await materialsResponse.json()
        setMaterialsByCategory(materialsData.data || [])

        setLoading(false)
      } catch (error) {
        console.error('Erro ao carregar dados:', error)
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#A28DFF', '#FF69B4', '#3CB371', '#BA55D3']

  if (loading) {
    return <div className="text-center py-8">Carregando dados do Dashboard...</div>
  }

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Dashboard</h2>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="bg-gray-900 border-gray-700 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Joias</CardTitle>
              <Diamond className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_jewelry}</div>
            </CardContent>
          </Card>
          <Card className="bg-gray-900 border-gray-700 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Materiais</CardTitle>
              <Gem className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_materials}</div>
            </CardContent>
          </Card>
          <Card className="bg-gray-900 border-gray-700 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Encomendas</CardTitle>
              <ShoppingBag className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_orders}</div>
            </CardContent>
          </Card>
          <Card className="bg-gray-900 border-gray-700 text-white">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Estoque Baixo</CardTitle>
              <Package className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.low_stock_items}</div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-gray-900 border-gray-700 text-white">
          <CardHeader>
            <CardTitle>Joias por Tipo</CardTitle>
            <CardDescription>Distribuição das joias cadastradas por tipo.</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={jewelryByType}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                  nameKey="type"
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                >
                  {jewelryByType.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value} joias`} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="bg-gray-900 border-gray-700 text-white">
          <CardHeader>
            <CardTitle>Materiais por Categoria</CardTitle>
            <CardDescription>Distribuição dos materiais por categoria.</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={materialsByCategory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis dataKey="category" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip formatter={(value) => `${value} materiais`} />
                <Bar dataKey="count" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  // Estados dos modais da Lua (independentes do chat)
  const [showFuncionariosModal, setShowFuncionariosModal] = useState(false);
  const [funcionariosData, setFuncionariosData] = useState([]);
  
  const [showVendasModal, setShowVendasModal] = useState(false);
  const [vendasData, setVendasData] = useState([]);
  
  const [showEncomendasModal, setShowEncomendasModal] = useState(false);
  const [encomendasData, setEncomendasData] = useState([]);
  
  const [showValesModal, setShowValesModal] = useState(false);
  const [valesData, setValesData] = useState([]);
  
  const [showEnergiaModal, setShowEnergiaModal] = useState(false);
  const [energiaData, setEnergiaData] = useState({});

  useEffect(() => {
    // Verifica se há um token no localStorage ou em cookies
    const token = localStorage.getItem('authToken')
    if (token) {
      setIsLoggedIn(true)
    }

    // Listener para comandos de voz JARVIS (independente do chat)
    const handleVoiceCommand = (event) => {
      const { data } = event.detail;
      console.log('🤖 JARVIS - Processando comando de voz:', data);
      
      if (data.show_in_interface && data.data) {
        console.log('🤖 JARVIS - Abrindo modal direto na tela principal');
        
        if (data.tipo === 'funcionarios') {
          setFuncionariosData(data.data);
          setShowFuncionariosModal(true);
        } else if (data.tipo === 'vendas') {
          setVendasData(data.data);
          setShowVendasModal(true);
        } else if (data.tipo === 'encomendas') {
          setEncomendasData(data.data);
          setShowEncomendasModal(true);
        } else if (data.tipo === 'vales') {
          setValesData(data.data);
          setShowValesModal(true);
        } else if (data.tipo === 'energia') {
          setEnergiaData(data.data);
          setShowEnergiaModal(true);
        }
      }
    };

    window.addEventListener('jarvisCommand', handleVoiceCommand);
    
    return () => {
      window.removeEventListener('jarvisCommand', handleVoiceCommand);
    };
  }, [])

  const handleLogin = (token) => {
    localStorage.setItem('authToken', token)
    setIsLoggedIn(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('authToken')
    setIsLoggedIn(false)
  }

  if (!isLoggedIn) {
    return <LoginScreen onLogin={handleLogin} />
  }

  return (
    <Router>
      <ModalProvider>
        <Layout handleLogout={handleLogout}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/clientes" element={<Clientes />} />
            <Route path="/funcionarios" element={<Funcionarios />} />
            <Route path="/joias-material" element={<JoiasMaterial />} />
            <Route path="/joias-materiais-pedras-rel" element={<JoiasMateriaisPedrasRel />} />
            <Route path="/joias-pedras" element={<JoiasPedras />} />
            <Route path="/joias-tamanhos" element={<JoiasTamanhos />} />
            <Route path="/caixa" element={<Caixa />} />
            <Route path="/custos" element={<Custos />} />
            <Route path="/descontos" element={<Descontos />} />
            <Route path="/entradas" element={<Entradas />} />
            <Route path="/impostos" element={<Impostos />} />
            <Route path="/vales" element={<Vales />} />
            <Route path="/folha-pagamento" element={<FolhaPagamento />} />
            <Route path="/pagamentos" element={<Pagamentos />} />
            <Route path="/prazos" element={<Prazos />} />
            <Route path="/encomendas" element={<Encomendas />} />
            <Route path="/encomendas-joias" element={<EncomendasJoias />} />
            <Route path="/estoque" element={<Estoque />} />
            <Route path="/estoque-filtros" element={<EstoqueFiltros />} />
            <Route path="/cartas" element={<Cartas />} />
            <Route path="/notas" element={<Notas />} />
            <Route path="/erros-ao-colar" element={<ErrosAoColar />} />
            <Route path="/joias" element={<Joias />} />
            <Route path="/padroes" element={<Padroes />} />
            <Route path="/dashboard-editavel" element={<DashboardEditavel />} />
            <Route path="/assistant" element={<Assistant />} />
            <Route path="/admin" element={<Assistant />} /> { /* Temporário, Painel da Lua ainda não existe */ }
          </Routes>
        </Layout>
        <ValeModal />
        <EncomendasModal />
        <InventoryModal />
        <SalesModal />
        <PdfHistoryModal />
        
        {/* Modais da Lua JARVIS - Independentes do chat */}
        <FuncionariosModal
          isOpen={showFuncionariosModal}
          onClose={() => setShowFuncionariosModal(false)}
          funcionarios={funcionariosData}
        />
        
        <VendasModal
          isOpen={showVendasModal}
          onClose={() => setShowVendasModal(false)}
          vendas={vendasData}
        />
        
        <EncomendasLuaModal
          isOpen={showEncomendasModal}
          onClose={() => setShowEncomendasModal(false)}
          encomendas={encomendasData}
        />
        
        <ValesLuaModal
          isOpen={showValesModal}
          onClose={() => setShowValesModal(false)}
          vales={valesData}
        />
        
        <EnergiaModal
          isOpen={showEnergiaModal}
          onClose={() => setShowEnergiaModal(false)}
          energiaData={energiaData}
        />
      </ModalProvider>
    </Router>
  )
}

export default App


