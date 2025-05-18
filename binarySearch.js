const valueToFind = 77;
const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20];


const binarySearch = (numbers, valueToFind) => {
    let left = 0;
    let right = numbers.length - 1;

    while (left <= right) {
        const middleIndex = Math.floor((left + right) / 2);

        if (numbers[middleIndex] === valueToFind) {
            return middleIndex;
        } else if (numbers[middleIndex] < valueToFind) {
            left = middleIndex + 1;
        } else {
            right = middleIndex - 1;
        }
    }
    return -1
}

const result = binarySearch(numbers, valueToFind);
if (result === -1) {
    console.log(`Value ${valueToFind} not found in the array, index: ${result}.`);
} else {
    console.log(`Value ${valueToFind} found at index ${result} in the array.`);
}