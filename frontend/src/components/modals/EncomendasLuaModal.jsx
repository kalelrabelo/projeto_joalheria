import React from 'react';
import { X } from 'lucide-react';

const EncomendasLuaModal = ({ isOpen, onClose, encomendas }) => {
  if (!isOpen) return null;

  const total = encomendas?.reduce((sum, encomenda) => sum + (encomenda.valor || 0), 0) || 0;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-800">📦 Encomendas</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <X size={24} />
          </button>
        </div>
        
        <div className="mb-4 p-4 bg-blue-50 rounded-lg">
          <p className="text-lg font-semibold text-blue-800">
            Total: R$ {total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
          </p>
          <p className="text-sm text-blue-600">
            {encomendas?.length || 0} encomendas encontradas
          </p>
        </div>
        
        <div className="grid gap-4">
          {encomendas && encomendas.length > 0 ? (
            encomendas.map((encomenda, index) => (
              <div key={encomenda.id || index} className="bg-gray-50 p-4 rounded-lg border">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Cliente:</label>
                    <p className="text-lg font-semibold text-gray-800">{encomenda.cliente}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Item:</label>
                    <p className="text-gray-800">{encomenda.item}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Valor:</label>
                    <p className="text-green-600 font-semibold">
                      R$ {(encomenda.valor || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Status:</label>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      encomenda.status === 'pendente' 
                        ? 'bg-yellow-100 text-yellow-800' 
                        : encomenda.status === 'em_producao'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {encomenda.status}
                    </span>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              Nenhuma encomenda encontrada
            </div>
          )}
        </div>
        
        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
};

export default EncomendasLuaModal;

