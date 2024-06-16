import numpy as np
import matplotlib.pyplot as plt
import csv

def csvread():
    csv_name = "C:\\Users\\alind\\neu-underwater-robotics\surface\sturgeon_test.csv"
    with open(csv_name, 'r') as csv_file:

        header1 = next(csv_file)
        header2 = next(csv_file)
        header3 = next(csv_file)
        reader = csv.reader(csv_file)

        days = range(1, 16)

        for row in reader:
            receiver = list()
            row = row[2:]
            for element in row:
                receiver.append(element)
            
            plt.plot(days, receiver)
        
        plt.xlabel('Day')
        plt.ylabel('# of Sturgeon')
        plt.title('Number of Sturgeon detected at each receiver over time', loc='center')
        plt.legend(['Receiver 1', 'Receiver 2', 'Receiver 3'])
        plt.xticks(days)
        plt.grid(True)

        plt.show()

        

def uiread():
    receiver1 = input("Enter Receiver 1's values for days 1-15: ")
    receiver1_list = list(map(int, receiver1.split()))
    receiver2 = input("Enter Receiver 2's values for days 1-15: ")
    receiver2_list = list(map(int, receiver2.split())) 
    receiver3 = input("Enter Receiver 3's values for days 1-15: ")
    receiver3_list = list(map(int, receiver3.split()))

    day_list = range(1, 16)

    plt.plot(day_list, receiver1_list, day_list, receiver2_list, day_list, receiver3_list)
    plt.xlabel('Day')
    plt.ylabel('# of Sturgeon')
    plt.title('Number of Sturgeon detected at each receiver over time', loc='center')
    plt.legend(['Receiver 1', 'Receiver 2', 'Receiver 3'])
    plt.xticks(day_list)
    plt.grid(True)

    plt.show()





def main():
    choice = input("Is there a CSV? (Y/N): ")
    if choice == 'N' or choice == 'n':
        uiread()
    elif choice == 'Y' or choice == 'y':
        csvread()
    elif choice == "e":
        exit()
    else:
     print("Invalid input.")
      

main()



