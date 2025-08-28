import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table.jsx';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx';
import { Label } from '@/components/ui/label.jsx';
import { Trash2, Plus, Edit, Image as ImageIcon, User } from 'lucide-react';
import FuncionarioDetalhesModal from './modals/FuncionarioDetalhesModal.jsx';
import axios from 'axios';

function Funcionarios() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isDetailsDialogOpen, setIsDetailsDialogOpen] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [formData, setFormData] = useState({
    id_funcionario: '',
    nome_usuario: '',
    senha: '',
    cpf: '',
    role: '',
    salary: '',
    imageUrl: ''
  });

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const response = await axios.get("/api/employees");
      setEmployees(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Erro ao buscar funcionários:", error);
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingEmployee) {
        await axios.put(`/api/employees/${editingEmployee.id_funcionario}`, formData);
      } else {
        await axios.post("/api/employees", formData);
      }
      fetchEmployees(); // Recarrega os dados após a operação
      setIsDialogOpen(false);
      setEditingEmployee(null);
      setFormData({ id_funcionario: '', nome_usuario: '', senha: '', cpf: '', role: '', salary: '', imageUrl: '' });
    } catch (error) {
      console.error("Erro ao salvar funcionário:", error);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Tem certeza que deseja excluir este funcionário?")) {
      try {
        await axios.delete(`/api/employees/${id}`);
        fetchEmployees(); // Recarrega os dados após a exclusão
      } catch (error) {
        console.error("Erro ao excluir funcionário:", error);
      }
    }
  };

  const handleEdit = (employee) => {
    setEditingEmployee(employee);
    setFormData({
      id_funcionario: employee.id_funcionario,
      nome_usuario: employee.nome_usuario,
      senha: employee.senha,
      cpf: employee.cpf || '',
      role: employee.role || '',
      salary: employee.salary || '',
      imageUrl: employee.imageUrl || ''
    });
    setIsDialogOpen(true);
  };

  const handleViewDetails = (employee) => {
    setSelectedEmployee(employee);
    setIsDetailsDialogOpen(true);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData(prev => ({
          ...prev,
          imageUrl: reader.result
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Funcionários</h2>
          <p className="text-gray-600">Gerenciamento de informações de funcionários.</p>
        </div>
        
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => {
              setEditingEmployee(null);
              setFormData({ id_funcionario: '', nome_usuario: '', senha: '', cpf: '', role: '', salary: '', imageUrl: '' });
            }}>
              <Plus className="h-4 w-4 mr-2" />
              Novo Funcionário
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingEmployee ? 'Editar Funcionário' : 'Novo Funcionário'}
              </DialogTitle>
              <DialogDescription>
                Preencha as informações do funcionário.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="nome_usuario" className="text-right">
                    Nome de Usuário
                  </Label>
                  <Input
                    id="nome_usuario"
                    name="nome_usuario"
                    value={formData.nome_usuario}
                    onChange={handleInputChange}
                    className="col-span-3"
                    required
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="senha" className="text-right">
                    Senha
                  </Label>
                  <Input
                    id="senha"
                    name="senha"
                    value={formData.senha}
                    onChange={handleInputChange}
                    className="col-span-3"
                    required
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="cpf" className="text-right">
                    CPF
                  </Label>
                  <Input
                    id="cpf"
                    name="cpf"
                    value={formData.cpf}
                    onChange={handleInputChange}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="role" className="text-right">
                    Cargo
                  </Label>
                  <Input
                    id="role"
                    name="role"
                    value={formData.role}
                    onChange={handleInputChange}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="salary" className="text-right">
                    Salário
                  </Label>
                  <Input
                    id="salary"
                    name="salary"
                    type="number"
                    step="0.01"
                    value={formData.salary}
                    onChange={handleInputChange}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="imageUrl" className="text-right">
                    Imagem
                  </Label>
                  <Input
                    id="imageUrl"
                    name="imageUrl"
                    type="file"
                    onChange={handleImageUpload}
                    className="col-span-3"
                  />
                  {formData.imageUrl && (
                    <div className="col-span-4 flex justify-center mt-2">
                      <img src={formData.imageUrl} alt="Preview" className="h-24 w-24 object-cover rounded-full" />
                    </div>
                  )}
                </div>
              </div>
              <DialogFooter>
                <Button type="submit">
                  {editingEmployee ? 'Atualizar' : 'Criar'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Modal de Detalhes do Funcionário - Estilo Carteira de Identidade */}
        <FuncionarioDetalhesModal
          funcionario={selectedEmployee}
          isOpen={isDetailsDialogOpen}
          onClose={() => {
            setIsDetailsDialogOpen(false);
            setSelectedEmployee(null);
          }}
          onSave={(funcionarioAtualizado) => {
            // Atualizar funcionário na lista
            setEmployees(prev => prev.map(emp => 
              emp.id === funcionarioAtualizado.id ? funcionarioAtualizado : emp
            ));
            console.log('Funcionário atualizado:', funcionarioAtualizado);
          }}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Lista de Funcionários</CardTitle>
          <CardDescription>
            Total de {employees.length} funcionários cadastrados
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Nome de Usuário</TableHead>
                <TableHead>CPF</TableHead>
                <TableHead>Cargo</TableHead>
                <TableHead>Salário</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {employees.map((employee) => (
                <TableRow key={employee.id_funcionario} onClick={() => handleViewDetails(employee)} className="cursor-pointer hover:bg-gray-100">
                  <TableCell>{employee.id_funcionario}</TableCell>
                  <TableCell>{employee.nome_usuario}</TableCell>
                  <TableCell>{employee.cpf || '-'}</TableCell>
                  <TableCell>{employee.role || '-'}</TableCell>
                  <TableCell>
                    {employee.salary ? `R$ ${parseFloat(employee.salary).toFixed(2)}` : '-'}
                  </TableCell>
                  <TableCell onClick={(e) => e.stopPropagation()}> {/* Prevent row click from triggering when clicking buttons */}
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEdit(employee)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDelete(employee.id_funcionario)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

export default Funcionarios;


