export declare const indentCodeSnippet: (decodedSnippet: string, indentCount: number) => string;
export declare const createArrayFromMultilineString: (multilineString: string) => string[];
export declare const createMultilineStringFromArray: (array: string[] | string[][]) => string;
export declare const removeEmptyLines: (array: string[]) => string[];
export declare const insertClassDocString: (array: string[], appName: string) => void;
export declare const delay: (ms: number) => Promise<unknown>;
export declare const decode: (string: string) => string;
export declare const encode: (string: string) => string;
export interface DataPointDefinition {
    path: string;
    required: string;
    access: string;
}
export interface VehicleModel {
    src: string;
    datapoints: DataPointDefinition[];
}
export interface AppManifest {
    name: string;
    vehicleModel: VehicleModel;
    runtime: string[];
}
