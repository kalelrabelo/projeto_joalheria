import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import LuaDashboardIntegration from './LuaDashboardIntegration';
import VoiceDashboardIntegration from './VoiceDashboardIntegration';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Filter, 
  BarChart3, 
  Table, 
  TrendingUp, 
  Settings,
  Grid,
  Save,
  RefreshCw,
  Bot,
  Mic
} from 'lucide-react';

const DashboardEditavel = () => {
  const [widgets, setWidgets] = useState([]);
  const [filtros, setFiltros] = useState({});
  const [grupos, setGrupos] = useState({});
  const [templates, setTemplates] = useState([]);
  const [modoEdicao, setModoEdicao] = useState(false);
  const [widgetSelecionado, setWidgetSelecionado] = useState(null);
  const [filtrosAtivos, setFiltrosAtivos] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    carregarDados();
  }, []);

  const carregarDados = async () => {
    setLoading(true);
    try {
      // Carregar filtros disponíveis
      const resFiltros = await fetch('http://localhost:5000/api/dashboard/filters');
      const filtrosData = await resFiltros.json();
      if (filtrosData.status === 'success') {
        setFiltros(filtrosData.data);
      }

      // Carregar grupos e subgrupos
      const resGrupos = await fetch('http://localhost:5000/api/dashboard/groups');
      const gruposData = await resGrupos.json();
      if (gruposData.status === 'success') {
        setGrupos(gruposData.data);
      }

      // Carregar templates
      const resTemplates = await fetch('http://localhost:5000/api/dashboard/templates');
      const templatesData = await resTemplates.json();
      if (templatesData.status === 'success') {
        setTemplates(templatesData.data);
      }

      // Carregar widgets do usuário (usando ID fixo para demo)
      const resWidgets = await fetch('http://localhost:5000/api/dashboard/widgets?user_id=1');
      const widgetsData = await resWidgets.json();
      if (widgetsData.status === 'success') {
        setWidgets(widgetsData.data);
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    }
    setLoading(false);
  };

  const adicionarWidget = async (template) => {
    try {
      const novoWidget = {
        titulo: template.nome || template.titulo,
        tipo: template.tipo,
        configuracao: template.configuracao,
        grupo: template.grupo,
        subgrupo: template.subgrupo,
        usuario_id: 1, // ID fixo para demo
        posicao_x: 0,
        posicao_y: 0,
        largura: 4,
        altura: 3
      };

      const response = await fetch('http://localhost:5000/api/dashboard/widgets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(novoWidget),
      });

      const data = await response.json();
      if (data.status === 'success') {
        setWidgets([...widgets, data.data]);
        // Carregar dados do widget recém-criado
        setTimeout(() => carregarDadosWidget(data.data.id), 500);
      }
    } catch (error) {
      console.error('Erro ao adicionar widget:', error);
    }
  };

  const adicionarWidgetViaLua = (widgetSuggestion) => {
    adicionarWidget(widgetSuggestion);
  };

  const removerWidget = async (widgetId) => {
    try {
      const response = await fetch(`http://localhost:5000/api/dashboard/widgets/${widgetId}`, {
        method: 'DELETE',
      });

      const data = await response.json();
      if (data.status === 'success') {
        setWidgets(widgets.filter(w => w.id !== widgetId));
      }
    } catch (error) {
      console.error('Erro ao remover widget:', error);
    }
  };

  const aplicarFiltros = (novosFiltros) => {
    setFiltrosAtivos(novosFiltros);
    // Recarregar dados dos widgets com os novos filtros
    widgets.forEach(widget => {
      carregarDadosWidget(widget.id, novosFiltros);
    });
  };

  const carregarDadosWidget = async (widgetId, filtrosPersonalizados = {}) => {
    try {
      const params = new URLSearchParams(filtrosPersonalizados);
      const response = await fetch(`http://localhost:5000/api/dashboard/widgets/${widgetId}/data?${params}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        // Atualizar dados do widget
        setWidgets(widgets.map(w => 
          w.id === widgetId ? { ...w, dados: data.data } : w
        ));
      }
    } catch (error) {
      console.error('Erro ao carregar dados do widget:', error);
    }
  };

  const renderWidget = (widget) => {
    const { tipo, titulo, dados } = widget;

    switch (tipo) {
      case 'comparison':
        return (
          <Card key={widget.id} className="h-full">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{titulo}</CardTitle>
              {modoEdicao && (
                <div className="flex gap-1">
                  <Button size="sm" variant="outline" onClick={() => setWidgetSelecionado(widget)}>
                    <Edit className="h-3 w-3" />
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => removerWidget(widget.id)}>
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              )}
            </CardHeader>
            <CardContent>
              {dados ? (
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Mês Atual:</span>
                    <span className="font-bold">R$ {dados.mes_atual?.valor?.toFixed(2) || '0,00'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Mês Anterior:</span>
                    <span className="font-bold">R$ {dados.mes_anterior?.valor?.toFixed(2) || '0,00'}</span>
                  </div>
                  {dados.diferenca !== undefined && (
                    <div className="flex justify-between">
                      <span>Diferença:</span>
                      <span className={`font-bold ${dados.diferenca >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {dados.diferenca >= 0 ? '+' : ''}R$ {dados.diferenca.toFixed(2)}
                      </span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center text-gray-500">Carregando dados...</div>
              )}
            </CardContent>
          </Card>
        );

      case 'metric':
        return (
          <Card key={widget.id} className="h-full">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{titulo}</CardTitle>
              {modoEdicao && (
                <div className="flex gap-1">
                  <Button size="sm" variant="outline" onClick={() => setWidgetSelecionado(widget)}>
                    <Edit className="h-3 w-3" />
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => removerWidget(widget.id)}>
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              )}
            </CardHeader>
            <CardContent>
              {dados ? (
                <div className="space-y-2">
                  <div className="text-2xl font-bold">
                    R$ {dados.valor?.toFixed(2) || dados.total_receitas?.toFixed(2) || '0,00'}
                  </div>
                  {dados.lucro_bruto !== undefined && (
                    <div className="space-y-1">
                      <div className="text-sm text-gray-600">
                        Lucro: R$ {dados.lucro_bruto.toFixed(2)}
                      </div>
                      <div className="text-sm text-gray-600">
                        Margem: {dados.margem_lucro.toFixed(1)}%
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center text-gray-500">Carregando dados...</div>
              )}
            </CardContent>
          </Card>
        );

      case 'table':
        return (
          <Card key={widget.id} className="h-full">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{titulo}</CardTitle>
              {modoEdicao && (
                <div className="flex gap-1">
                  <Button size="sm" variant="outline" onClick={() => setWidgetSelecionado(widget)}>
                    <Edit className="h-3 w-3" />
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => removerWidget(widget.id)}>
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              )}
            </CardHeader>
            <CardContent>
              {dados && dados.length > 0 ? (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {dados.map((item, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <div>
                        <div className="font-medium">{item.funcionario_nome || item.cliente || 'N/A'}</div>
                        <div className="text-sm text-gray-600">{item.motivo || item.observacoes || ''}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold">R$ {item.valor?.toFixed(2) || item.valor_total?.toFixed(2) || '0,00'}</div>
                        <div className="text-sm text-gray-600">
                          {new Date(item.data_vale || item.data_venda).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-500">Nenhum dado disponível</div>
              )}
            </CardContent>
          </Card>
        );

      default:
        return (
          <Card key={widget.id} className="h-full">
            <CardHeader>
              <CardTitle>{titulo}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center text-gray-500">Tipo de widget não suportado</div>
            </CardContent>
          </Card>
        );
    }
  };

  const renderFiltros = () => {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Filtros
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="funcionarios">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="funcionarios">Funcionários</TabsTrigger>
              <TabsTrigger value="vendas">Vendas</TabsTrigger>
              <TabsTrigger value="joias">Joias</TabsTrigger>
              <TabsTrigger value="financeiro">Financeiro</TabsTrigger>
            </TabsList>
            
            {Object.entries(filtros).map(([grupo, filtrosGrupo]) => (
              <TabsContent key={grupo} value={grupo} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  {filtrosGrupo.map((filtro, index) => (
                    <div key={index}>
                      <label className="text-sm font-medium">{filtro.nome}</label>
                      {filtro.tipo === 'select' ? (
                        <Select onValueChange={(value) => {
                          setFiltrosAtivos({
                            ...filtrosAtivos,
                            [filtro.campo]: value
                          });
                        }}>
                          <SelectTrigger>
                            <SelectValue placeholder={`Selecione ${filtro.nome}`} />
                          </SelectTrigger>
                          <SelectContent>
                            {filtro.opcoes?.map((opcao, idx) => (
                              <SelectItem key={idx} value={opcao.value || opcao}>
                                {opcao.label || opcao}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      ) : filtro.tipo === 'date_range' ? (
                        <div className="flex gap-2">
                          <Input 
                            type="date" 
                            placeholder="Data início"
                            onChange={(e) => {
                              setFiltrosAtivos({
                                ...filtrosAtivos,
                                [`${filtro.campo}_inicio`]: e.target.value
                              });
                            }}
                          />
                          <Input 
                            type="date" 
                            placeholder="Data fim"
                            onChange={(e) => {
                              setFiltrosAtivos({
                                ...filtrosAtivos,
                                [`${filtro.campo}_fim`]: e.target.value
                              });
                            }}
                          />
                        </div>
                      ) : (
                        <Input 
                          placeholder={`Digite ${filtro.nome}`}
                          onChange={(e) => {
                            setFiltrosAtivos({
                              ...filtrosAtivos,
                              [filtro.campo]: e.target.value
                            });
                          }}
                        />
                      )}
                    </div>
                  ))}
                </div>
                <Button onClick={() => aplicarFiltros(filtrosAtivos)}>
                  Aplicar Filtros
                </Button>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard Editável</h1>
        <div className="flex gap-2">
          <Button 
            variant={modoEdicao ? "default" : "outline"} 
            onClick={() => setModoEdicao(!modoEdicao)}
          >
            <Edit className="h-4 w-4 mr-2" />
            {modoEdicao ? 'Sair da Edição' : 'Modo Edição'}
          </Button>
          <Button onClick={carregarDados} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Badge variant="outline" className="flex items-center gap-1">
            <Mic className="h-3 w-3" />
            Comandos de Voz Ativos
          </Badge>
        </div>
      </div>

      {modoEdicao && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                Adicionar Widget
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-4">
                {templates.map((template) => (
                  <Card key={template.id} className="cursor-pointer hover:bg-gray-50" onClick={() => adicionarWidget(template)}>
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 mb-2">
                        {template.tipo === 'comparison' && <TrendingUp className="h-4 w-4" />}
                        {template.tipo === 'metric' && <BarChart3 className="h-4 w-4" />}
                        {template.tipo === 'table' && <Table className="h-4 w-4" />}
                        <span className="font-medium">{template.nome}</span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{template.descricao}</p>
                      <div className="flex gap-1">
                        <Badge variant="secondary">{grupos[template.grupo]?.nome || template.grupo}</Badge>
                        <Badge variant="outline">{template.subgrupo}</Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>

          <LuaDashboardIntegration onAddWidget={adicionarWidgetViaLua} />
          
          <VoiceDashboardIntegration onAddWidget={adicionarWidgetViaLua} />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          {renderFiltros()}
        </div>
        
        <div className="lg:col-span-3">
          {widgets.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {widgets.map(widget => renderWidget(widget))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Grid className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhum widget adicionado</h3>
                <p className="text-gray-600 mb-4">
                  {modoEdicao 
                    ? "Adicione widgets usando os templates acima para começar a visualizar seus dados."
                    : "Ative o modo de edição para adicionar widgets ao seu dashboard."
                  }
                </p>
                {!modoEdicao && (
                  <Button onClick={() => setModoEdicao(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Adicionar Primeiro Widget
                  </Button>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardEditavel;

