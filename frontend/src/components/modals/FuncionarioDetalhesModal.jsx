import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { User, Phone, Mail, Calendar, DollarSign, MapPin, Camera, Edit, Save, X } from 'lucide-react';

const FuncionarioDetalhesModal = ({ funcionario, isOpen, onClose, onSave }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    nome_completo: funcionario?.nome_completo || funcionario?.nome || funcionario?.nome_usuario || '',
    nome_usuario: funcionario?.nome_usuario || '',
    email: funcionario?.email || '',
    telefone: funcionario?.telefone || '',
    endereco: funcionario?.endereco || '',
    cargo: funcionario?.cargo || '',
    salario_base: funcionario?.salario_base || funcionario?.salario || 0,
    data_admissao: funcionario?.data_admissao || '',
    cpf: funcionario?.cpf || '',
    rg: funcionario?.rg || '',
    foto: funcionario?.foto || null,
    status: funcionario?.status || 'ativo',
    horas_extra: funcionario?.horas_extra || 0
  });

  if (!funcionario) return null;

  const handleSave = () => {
    if (onSave) {
      onSave({ ...funcionario, ...editData });
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditData({
      nome: funcionario?.nome || funcionario?.nome_usuario || '',
      nome_usuario: funcionario?.nome_usuario || '',
      email: funcionario?.email || '',
      telefone: funcionario?.telefone || '',
      endereco: funcionario?.endereco || '',
      cargo: funcionario?.cargo || '',
      salario: funcionario?.salario || 0,
      data_admissao: funcionario?.data_admissao || '',
      cpf: funcionario?.cpf || '',
      rg: funcionario?.rg || '',
      foto: funcionario?.foto || null,
      status: funcionario?.status || 'ativo'
    });
    setIsEditing(false);
  };

  const formatarMoeda = (valor) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor || 0);
  };

  const formatarData = (data) => {
    if (!data) return 'Não informado';
    try {
      return new Date(data).toLocaleDateString('pt-BR');
    } catch {
      return data;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-2xl">
            <User className="h-6 w-6" />
            Carteira de Funcionário
            {!isEditing && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(true)}
                className="ml-auto"
              >
                <Edit className="h-4 w-4 mr-2" />
                Editar
              </Button>
            )}
            {isEditing && (
              <div className="ml-auto flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCancel}
                >
                  <X className="h-4 w-4 mr-2" />
                  Cancelar
                </Button>
                <Button
                  size="sm"
                  onClick={handleSave}
                >
                  <Save className="h-4 w-4 mr-2" />
                  Salvar
                </Button>
              </div>
            )}
          </DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Foto e Informações Básicas */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-center">Foto do Funcionário</CardTitle>
            </CardHeader>
            <CardContent className="text-center">
              <div className="relative mx-auto w-32 h-32 mb-4">
                {editData.foto ? (
                  <img
                    src={editData.foto}
                    alt={editData.nome}
                    className="w-full h-full rounded-full object-cover border-4 border-gray-200"
                  />
                ) : (
                  <div className="w-full h-full rounded-full bg-gray-200 flex items-center justify-center border-4 border-gray-300">
                    <User className="h-16 w-16 text-gray-400" />
                  </div>
                )}
                {isEditing && (
                  <Button
                    size="sm"
                    className="absolute bottom-0 right-0 rounded-full"
                    onClick={() => {
                      // Implementar upload de foto
                      const input = document.createElement('input');
                      input.type = 'file';
                      input.accept = 'image/*';
                      input.onchange = (e) => {
                        const file = e.target.files[0];
                        if (file) {
                          const reader = new FileReader();
                          reader.onload = (e) => {
                            setEditData(prev => ({ ...prev, foto: e.target.result }));
                          };
                          reader.readAsDataURL(file);
                        }
                      };
                      input.click();
                    }}
                  >
                    <Camera className="h-3 w-3" />
                  </Button>
                )}
              </div>
              
              <div className="space-y-2">
                <Badge 
                  variant={editData.status === 'ativo' ? 'default' : 'secondary'}
                  className="text-sm"
                >
                  {editData.status === 'ativo' ? '✅ Ativo' : '❌ Inativo'}
                </Badge>
                <p className="text-sm text-gray-600">ID: #{funcionario.id}</p>
              </div>
            </CardContent>
          </Card>

          {/* Informações Pessoais */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Informações Pessoais</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="nome">Nome Completo</Label>
                  {isEditing ? (
                    <Input
                      id="nome"
                      value={editData.nome}
                      onChange={(e) => setEditData(prev => ({ ...prev, nome: e.target.value }))}
                      placeholder="Nome completo do funcionário"
                    />
                  ) : (
                    <p className="text-lg font-semibold">{editData.nome || 'Não informado'}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="nome_usuario">Nome de Usuário</Label>
                  {isEditing ? (
                    <Input
                      id="nome_usuario"
                      value={editData.nome_usuario}
                      onChange={(e) => setEditData(prev => ({ ...prev, nome_usuario: e.target.value }))}
                      placeholder="Nome de usuário"
                    />
                  ) : (
                    <p className="text-lg font-semibold">@{editData.nome_usuario}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="cpf">CPF</Label>
                  {isEditing ? (
                    <Input
                      id="cpf"
                      value={editData.cpf}
                      onChange={(e) => setEditData(prev => ({ ...prev, cpf: e.target.value }))}
                      placeholder="000.000.000-00"
                    />
                  ) : (
                    <p>{editData.cpf || 'Não informado'}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="rg">RG</Label>
                  {isEditing ? (
                    <Input
                      id="rg"
                      value={editData.rg}
                      onChange={(e) => setEditData(prev => ({ ...prev, rg: e.target.value }))}
                      placeholder="00.000.000-0"
                    />
                  ) : (
                    <p>{editData.rg || 'Não informado'}</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Informações de Contato */}
          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Phone className="h-5 w-5" />
                Contato
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="email">E-mail</Label>
                  {isEditing ? (
                    <Input
                      id="email"
                      type="email"
                      value={editData.email}
                      onChange={(e) => setEditData(prev => ({ ...prev, email: e.target.value }))}
                      placeholder="email@exemplo.com"
                    />
                  ) : (
                    <p className="flex items-center gap-2">
                      <Mail className="h-4 w-4" />
                      {editData.email || 'Não informado'}
                    </p>
                  )}
                </div>

                <div>
                  <Label htmlFor="telefone">Telefone</Label>
                  {isEditing ? (
                    <Input
                      id="telefone"
                      value={editData.telefone}
                      onChange={(e) => setEditData(prev => ({ ...prev, telefone: e.target.value }))}
                      placeholder="(11) 99999-9999"
                    />
                  ) : (
                    <p className="flex items-center gap-2">
                      <Phone className="h-4 w-4" />
                      {editData.telefone || 'Não informado'}
                    </p>
                  )}
                </div>

                <div>
                  <Label htmlFor="endereco">Endereço</Label>
                  {isEditing ? (
                    <Input
                      id="endereco"
                      value={editData.endereco}
                      onChange={(e) => setEditData(prev => ({ ...prev, endereco: e.target.value }))}
                      placeholder="Endereço completo"
                    />
                  ) : (
                    <p className="flex items-center gap-2">
                      <MapPin className="h-4 w-4" />
                      {editData.endereco || 'Não informado'}
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Informações Profissionais */}
          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Informações Profissionais
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="cargo">Cargo</Label>
                  {isEditing ? (
                    <Input
                      id="cargo"
                      value={editData.cargo}
                      onChange={(e) => setEditData(prev => ({ ...prev, cargo: e.target.value }))}
                      placeholder="Cargo do funcionário"
                    />
                  ) : (
                    <p className="text-lg font-semibold">{editData.cargo || 'Não informado'}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="salario">Salário</Label>
                  {isEditing ? (
                    <Input
                      id="salario"
                      type="number"
                      value={editData.salario}
                      onChange={(e) => setEditData(prev => ({ ...prev, salario: parseFloat(e.target.value) || 0 }))}
                      placeholder="0.00"
                    />
                  ) : (
                    <p className="text-lg font-semibold text-green-600">
                      {formatarMoeda(editData.salario)}
                    </p>
                  )}
                </div>

                <div>
                  <Label htmlFor="data_admissao">Data de Admissão</Label>
                  {isEditing ? (
                    <Input
                      id="data_admissao"
                      type="date"
                      value={editData.data_admissao}
                      onChange={(e) => setEditData(prev => ({ ...prev, data_admissao: e.target.value }))}
                    />
                  ) : (
                    <p className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      {formatarData(editData.data_admissao)}
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default FuncionarioDetalhesModal;

