import React from 'react';

export const TesteTailwind: React.FC = () => {
  return (
    <div className="p-6 bg-red-500 text-white rounded-lg shadow-lg">
      <h1 className="text-2xl font-bold mb-4">Teste Tailwind CSS</h1>
      <div className="bg-blue-500 p-4 rounded">
        <p className="text-sm">Se você vê este texto em branco sobre fundo azul, o Tailwind está funcionando!</p>
      </div>
      <div className="grid grid-cols-2 gap-4 mt-4">
        <div className="bg-green-500 p-2 rounded">Verde</div>
        <div className="bg-yellow-500 p-2 rounded">Amarelo</div>
      </div>
    </div>
  );
};
