// types/chart-data.ts
export interface ChartData {
    labels: string[];
    datasets: {
        label: string;
        data: number[];
        color?: string;
    }[];
}

export interface ChartOptions {
    titulo?: string;
    subtitulo?: string;
    formatoValor?: 'moeda' | 'percentual' | 'numero';
    mostrarLegenda?: boolean;
    mostrarGrade?: boolean;
    alturaMinima?: number;
}
