import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Bot, Send, Plus, TrendingUp, BarChart3, Table } from 'lucide-react';

const LuaDashboardIntegration = ({ onAddWidget }) => {
  const [comando, setComando] = useState('');
  const [resposta, setResposta] = useState(null);
  const [loading, setLoading] = useState(false);

  const processarComando = async () => {
    if (!comando.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/dashboard/lua/command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ comando }),
      });

      const data = await response.json();
      setResposta(data);
    } catch (error) {
      console.error('Erro ao processar comando:', error);
      setResposta({
        status: 'error',
        message: 'Erro ao processar comando. Verifique a conexão com o servidor.'
      });
    }
    setLoading(false);
  };

  const adicionarWidgetSugerido = () => {
    if (resposta?.widget_suggestion && onAddWidget) {
      onAddWidget(resposta.widget_suggestion);
      setResposta(null);
      setComando('');
    }
  };

  const comandosExemplo = [
    "Lua, me mostre no dashboard conta de luz desse mês com o do mês passado e compare",
    "Lua me mostra o gasto e lucro desse mês no dashboard",
    "Lua me mostra no dashboard os últimos vales do mês"
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bot className="h-5 w-5" />
          Assistente LUA - Dashboard
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Input
            placeholder="Digite seu comando para a LUA..."
            value={comando}
            onChange={(e) => setComando(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && processarComando()}
          />
          <Button onClick={processarComando} disabled={loading}>
            <Send className="h-4 w-4" />
          </Button>
        </div>

        {/* Comandos de exemplo */}
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">Comandos de exemplo:</p>
          <div className="space-y-1">
            {comandosExemplo.map((exemplo, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                className="text-xs h-auto p-2 text-left justify-start"
                onClick={() => setComando(exemplo)}
              >
                {exemplo}
              </Button>
            ))}
          </div>
        </div>

        {/* Resposta da LUA */}
        {resposta && (
          <Card className={`border-l-4 ${
            resposta.status === 'success' ? 'border-l-green-500' : 
            resposta.status === 'error' ? 'border-l-red-500' : 'border-l-blue-500'
          }`}>
            <CardContent className="p-4">
              <p className="text-sm mb-3">{resposta.message}</p>
              
              {resposta.data && (
                <div className="bg-gray-50 p-3 rounded mb-3">
                  <pre className="text-xs overflow-auto">
                    {JSON.stringify(resposta.data, null, 2)}
                  </pre>
                </div>
              )}

              {resposta.widget_suggestion && (
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded">
                  <div className="flex items-center gap-2">
                    {resposta.widget_suggestion.tipo === 'comparison' && <TrendingUp className="h-4 w-4" />}
                    {resposta.widget_suggestion.tipo === 'metric' && <BarChart3 className="h-4 w-4" />}
                    {resposta.widget_suggestion.tipo === 'table' && <Table className="h-4 w-4" />}
                    <span className="font-medium">{resposta.widget_suggestion.titulo}</span>
                    <Badge variant="secondary">{resposta.widget_suggestion.tipo}</Badge>
                  </div>
                  <Button size="sm" onClick={adicionarWidgetSugerido}>
                    <Plus className="h-3 w-3 mr-1" />
                    Adicionar
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </CardContent>
    </Card>
  );
};

export default LuaDashboardIntegration;

