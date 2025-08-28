import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, X, ChevronLeft, ChevronRight, Filter } from 'lucide-react';
import { padroesData } from '../data/padroesData.js';

function Padroes() {
  const [selectedPattern, setSelectedPattern] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('todos');
  const [filteredPatterns, setFilteredPatterns] = useState([]);
  const [groupedPatterns, setGroupedPatterns] = useState({});
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12; // 12 padrões por página

  // Obter tipos únicos dos dados
  const uniqueTypes = [...new Set(padroesData.map(pattern => pattern.categoria).filter(Boolean))].sort();

  useEffect(() => {
    try {
      let filtered = padroesData.filter(pattern => {
        const matchesSearch = 
          (pattern.nome || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
          (pattern.categoria || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
          (pattern.colecao || '').toLowerCase().includes(searchTerm.toLowerCase());
        
        const matchesType = selectedType === 'todos' || pattern.categoria === selectedType;
        
        return matchesSearch && matchesType;
      });

      // Separar padrões com e sem imagem, depois ordenar
      const withImages = filtered.filter(pattern => pattern.imagem);
      const withoutImages = filtered.filter(pattern => !pattern.imagem);
      
      // Ordenar cada grupo por tipo e nome
      const sortPattern = (a, b) => {
        if (a.categoria !== b.categoria) {
          return (a.categoria || '').localeCompare(b.categoria || '');
        }
        return (a.nome || '').localeCompare(b.nome || '');
      };
      
      withImages.sort(sortPattern);
      withoutImages.sort(sortPattern);
      
      // Combinar: imagens primeiro, depois sem imagens
      const sorted = [...withImages, ...withoutImages];

      // Agrupar por tipo (10 por página por tipo)
      const grouped = sorted.reduce((acc, pattern) => {
        const type = pattern.categoria || 'Sem Categoria';
        if (!acc[type]) {
          acc[type] = [];
        }
        acc[type].push(pattern);
        return acc;
      }, {});

      setFilteredPatterns(sorted);
      setGroupedPatterns(grouped);
      setCurrentPage(1); // Resetar para a primeira página ao filtrar/ordenar
    } catch (error) {
      console.error('Erro ao filtrar padrões:', error);
      setFilteredPatterns([]);
      setGroupedPatterns({});
    }
  }, [searchTerm, selectedType]);

  const handlePatternClick = (pattern) => {
    setSelectedPattern(pattern);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedPattern(null);
  };

  const placeholderImage = '/images/placeholder.png'; // Caminho para a imagem de placeholder

  // Lógica de paginação
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filteredPatterns.slice(indexOfFirstItem, indexOfLastItem);

  const totalPages = Math.ceil(filteredPatterns.length / itemsPerPage);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white">Catálogo de Padrões</h2>
        <p className="text-gray-400">Organizados por tipo. Total: {filteredPatterns.length} padrões</p>
      </div>

      {/* Filtros */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search Bar */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Pesquisar padrões por nome, categoria ou coleção..."
            className="pl-10 bg-gray-800 border-gray-600 text-white placeholder-gray-400"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Filtro por Tipo */}
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-gray-400" />
          <Select value={selectedType} onValueChange={setSelectedType}>
            <SelectTrigger className="w-[200px] bg-gray-800 border-gray-600 text-white">
              <SelectValue placeholder="Filtrar por tipo" />
            </SelectTrigger>
            <SelectContent className="bg-gray-800 border-gray-600">
              <SelectItem value="todos" className="text-white hover:bg-gray-700">Todos os tipos</SelectItem>
              {uniqueTypes.map((type) => (
                <SelectItem key={type} value={type} className="text-white hover:bg-gray-700">
                  {type}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Exibição por grupos de tipo */}
      {selectedType === 'todos' ? (
        <div className="space-y-8">
          {Object.entries(groupedPatterns).map(([type, patterns]) => (
            <div key={type} className="space-y-4">
              <div className="flex items-center gap-3">
                <h3 className="text-2xl font-bold text-white">{type}</h3>
                <Badge variant="outline" className="border-gray-600 text-gray-300">
                  {patterns.length} {patterns.length === 1 ? 'item' : 'itens'}
                </Badge>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {patterns.map((pattern) => (
                  <Card key={pattern.id} className="cursor-pointer hover:shadow-lg transition-all duration-200 hover:scale-105 bg-gray-900 border-gray-600" onClick={() => handlePatternClick(pattern)}>
                    <CardHeader className="p-0">
                      <img 
                        src={pattern.imagem || placeholderImage} 
                        alt={pattern.nome} 
                        className="w-[140px] h-[140px] object-contain rounded-t-lg mx-auto"
                        onError={(e) => {
                          e.target.src = placeholderImage;
                        }}
                      />
                    </CardHeader>
                    <CardContent className="p-4">
                      <CardTitle className="text-lg mb-2 text-white">{pattern.nome}</CardTitle>
                      <div className="space-y-1 mb-3">
                        <p className="text-sm text-gray-400">Coleção: {pattern.colecao}</p>
                      </div>
                      <p className="text-lg font-bold text-blue-400">Consultar</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        // Exibição com paginação quando um tipo específico é selecionado
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {currentItems.map((pattern) => (
              <Card key={pattern.id} className="cursor-pointer hover:shadow-lg transition-all duration-200 hover:scale-105 bg-gray-900 border-gray-600" onClick={() => handlePatternClick(pattern)}>
                <CardHeader className="p-0">
                  <img 
                    src={pattern.imagem || placeholderImage} 
                    alt={pattern.nome} 
                    className="w-[140px] h-[140px] object-contain rounded-t-lg mx-auto"
                    onError={(e) => {
                      e.target.src = placeholderImage;
                    }}
                  />
                </CardHeader>
                <CardContent className="p-4">
                  <CardTitle className="text-lg mb-2 text-white">{pattern.nome}</CardTitle>
                  <div className="space-y-1 mb-3">
                    <Badge variant="secondary" className="mr-1 bg-gray-700 text-gray-200">{pattern.categoria}</Badge>
                    <p className="text-sm text-gray-400">Coleção: {pattern.colecao}</p>
                  </div>
                  <p className="text-lg font-bold text-blue-400">Consultar</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center space-x-2 mt-6">
              <Button
                variant="outline"
                size="icon"
                onClick={() => paginate(currentPage - 1)}
                disabled={currentPage === 1}
                className="bg-gray-800 border-gray-600 text-white hover:bg-gray-700"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="text-white">Página {currentPage} de {totalPages}</span>
              <Button
                variant="outline"
                size="icon"
                onClick={() => paginate(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="bg-gray-800 border-gray-600 text-white hover:bg-gray-700"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>
      )}

      {filteredPatterns.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-400 text-lg">Nenhum padrão encontrado com os critérios de pesquisa.</p>
        </div>
      )}

      {/* Modal for Pattern Details */}
      {selectedPattern && (
        <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
          <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto bg-gray-900 border-gray-600">
            <DialogHeader>
              <div className="flex justify-between items-start">
                <div>
                  <DialogTitle className="text-2xl text-white">{selectedPattern.nome}</DialogTitle>
                  <DialogDescription className="text-lg text-blue-400 font-semibold mt-1">
                    Consultar
                  </DialogDescription>
                </div>
                <Button variant="ghost" size="sm" onClick={closeModal} className="text-white hover:bg-gray-800">
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </DialogHeader>
            
            <div className="grid gap-6 py-4">
              {/* Main pattern details */}
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <img 
                    src={selectedPattern.imagem || placeholderImage} 
                    alt={selectedPattern.nome} 
                    className="w-[200px] h-[200px] object-contain rounded-lg shadow-md mx-auto"
                    onError={(e) => {
                      e.target.src = placeholderImage;
                    }}
                  />
                </div>
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-lg mb-2 text-white">Detalhes</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Tipo:</span>
                        <Badge variant="outline" className="border-gray-600 text-gray-200">{selectedPattern.categoria}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Coleção:</span>
                        <span className="font-medium text-white">{selectedPattern.colecao}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">ID:</span>
                        <span className="font-medium text-white">{selectedPattern.id}</span>
                      </div>
                    </div>
                  </div>
                  {selectedPattern.noticia && (
                    <div>
                      <h3 className="font-semibold text-lg mb-2 text-white">Especificações</h3>
                      <p className="text-gray-300 text-sm leading-relaxed">{selectedPattern.noticia}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}

export default Padroes;

