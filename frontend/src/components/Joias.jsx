import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Search, X, Filter } from 'lucide-react';
import { joiasData } from '../data/joiasData.js';

function Joias() {
  const [selectedJewelry, setSelectedJewelry] = useState(null);
  const [relatedJewelry, setRelatedJewelry] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredJewelry, setFilteredJewelry] = useState([]);
  const [allJewelryFlat, setAllJewelryFlat] = useState([]);
  const [mainJewelryList, setMainJewelryList] = useState([]); // Lista principal para exibição

  useEffect(() => {
    // Flatten the jewelry data to include all variants
    const flatJewelry = [];
    const mainJewelryOnly = []; // Array para exibir apenas uma joia por grupo
    
    joiasData.forEach(joia => {
      let isFirstVariant = true; // Flag para pegar apenas a primeira variante de cada grupo
      
      joia.variantes.forEach(variante => {
        const jewelryItem = {
          id: variante.id,
          name: variante.nome,
          category: joia.categoria,
          material: 'Prata', // Default material
          stone: joia.nome,
          price: variante.preco > 0 ? `€${variante.preco}` : 'Consultar',
          description: `${variante.nome} - ${joia.categoria}`,
          image: variante.imagem,
          available: variante.disponivel,
          parentId: joia.id // Adiciona o ID da joia pai para agrupar variantes
        };
        
        flatJewelry.push(jewelryItem);
        
        // Adiciona apenas a primeira variante de cada grupo para exibição principal
        if (isFirstVariant) {
          mainJewelryOnly.push(jewelryItem);
          isFirstVariant = false;
        }
      });
    });
    
    setAllJewelryFlat(flatJewelry); // Mantém todas as joias para busca nas relacionadas
    setMainJewelryList(mainJewelryOnly); // Lista principal para exibição
    setFilteredJewelry(mainJewelryOnly); // Exibe apenas uma joia por grupo
  }, []);

  useEffect(() => {
    const filtered = mainJewelryList.filter(jewelry =>
      jewelry.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      jewelry.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      jewelry.material.toLowerCase().includes(searchTerm.toLowerCase()) ||
      jewelry.stone.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredJewelry(filtered);
  }, [searchTerm, mainJewelryList]);

  const handleJewelryClick = (jewelry) => {
    setSelectedJewelry(jewelry);
    // Filter related jewelry based on category, material, or stone
    const related = allJewelryFlat.filter(item => 
      item.parentId === jewelry.parentId && 
      item.id !== jewelry.id
    ).slice(0, 6); // Limit to 6 related items
    setRelatedJewelry(related);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedJewelry(null);
    setRelatedJewelry([]);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white">Catálogo de Joias</h2>
        <p className="text-gray-400">Clique em uma joia para ver detalhes e itens relacionados.</p>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
        <Input
          placeholder="Pesquisar joias por nome, categoria, material ou pedra..."
          className="pl-10 bg-gray-800 border-gray-600 text-white placeholder-gray-400"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Jewelry Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {filteredJewelry.map((jewelry) => (
          <Card key={jewelry.id} className="cursor-pointer hover:shadow-lg transition-all duration-200 hover:scale-105 bg-gray-900 border-gray-600" onClick={() => handleJewelryClick(jewelry)}>
            <CardHeader className="p-0">
              <img src={jewelry.image} alt={jewelry.name} className="w-[140px] h-[140px] object-contain rounded-t-lg mx-auto" />
            </CardHeader>
            <CardContent className="p-4">
              <CardTitle className="text-lg mb-2 text-white">{jewelry.name}</CardTitle>
              <div className="space-y-1 mb-3">
                <Badge variant="secondary" className="mr-1 bg-gray-700 text-gray-200">{jewelry.category}</Badge>
                <p className="text-sm text-gray-400">Material: {jewelry.material}</p>
                <p className="text-sm text-gray-400">Pedra: {jewelry.stone}</p>
              </div>
              <p className="text-lg font-bold text-blue-400">{jewelry.price}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredJewelry.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-400 text-lg">Nenhuma joia encontrada com os critérios de pesquisa.</p>
        </div>
      )}

      {/* Modal for Jewelry Details */}
      {selectedJewelry && (
        <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
          <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto bg-gray-900 border-gray-600">
            <DialogHeader>
              <div className="flex justify-between items-start">
                <div>
                  <DialogTitle className="text-2xl text-white">{selectedJewelry.name}</DialogTitle>
                  <DialogDescription className="text-lg text-blue-400 font-semibold mt-1">
                    {selectedJewelry.price}
                  </DialogDescription>
                </div>
                <Button variant="ghost" size="sm" onClick={closeModal} className="text-white hover:bg-gray-800">
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </DialogHeader>
            
            <div className="grid gap-6 py-4">
              {/* Main jewelry details */}
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <img 
                    src={selectedJewelry.image} 
                    alt={selectedJewelry.name} 
                    className="w-[140px] h-[140px] object-contain rounded-lg shadow-md mx-auto" 
                  />
                </div>
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-lg mb-2 text-white">Detalhes</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Categoria:</span>
                        <Badge variant="outline" className="border-gray-600 text-gray-200">{selectedJewelry.category}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Material:</span>
                        <span className="font-medium text-white">{selectedJewelry.material}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Pedra:</span>
                        <span className="font-medium text-white">{selectedJewelry.stone}</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg mb-2 text-white">Descrição</h3>
                    <p className="text-gray-300">{selectedJewelry.description}</p>
                  </div>
                </div>
              </div>

              {/* Related jewelry section */}
              {relatedJewelry.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-xl font-semibold mb-4 flex items-center text-white">
                    <Filter className="h-5 w-5 mr-2" />
                    Variantes Disponíveis ({relatedJewelry.length})
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {relatedJewelry.map(item => (
                      <Card 
                        key={item.id} 
                        className="cursor-pointer hover:shadow-md transition-shadow bg-gray-800 border-gray-600" 
                        onClick={() => handleJewelryClick(item)}
                      >
                        <CardHeader className="p-0">
                          <img 
                            src={item.image} 
                            alt={item.name} 
                            className="w-[140px] h-[140px] object-contain rounded-t-lg mx-auto" 
                          />
                        </CardHeader>
                        <CardContent className="p-3">
                          <CardTitle className="text-sm mb-1 text-white">{item.name}</CardTitle>
                          <div className="space-y-1">
                            <Badge variant="secondary" className="text-xs bg-gray-700 text-gray-200">{item.category}</Badge>
                            <p className="text-xs text-gray-400">{item.material}</p>
                            <p className="text-sm font-semibold text-blue-400">{item.price}</p>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}

export default Joias;




