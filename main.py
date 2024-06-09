import struct
from global import GlobalVariables
from pipeline import Pipeline

def load_instructions(shred, input_file, log_file):
    with open(input_file, 'rb') as f:
        while True:
            data = f.read(4)
            if len(data) < 4:
                break
            
            instruction = struct.unpack('>I', data)[0]
            shred.raw_instruction_memory.append(instruction)

    with open(log_file, 'w') as log:
        for index, value in enumerate(shred.raw_instruction_memory):
            log.write(f"Index: {index}, Value: {value:08x}\n")
    
    return shred.raw_instruction_memory


def main():
    shred = GlobalVariables()

    input_file = input('Enter the path to the binary file: ')
    log_file = 'logs/instruction_memory.txt'

    shred.instruction_memory = load_instructions(shred, input_file, log_file)
    
    pipeline = Pipeline()
    pipeline.run(shred)

    print("Simulation complete. Check the logs folder for the output files.")

if __name__ == "__main__":  
    main()