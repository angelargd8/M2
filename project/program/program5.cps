function risky(): void {
    try {
        print("Trying risky operation");
        let x: integer = 10 / 0;  // operación que genera error
    } catch (e) {
        print("Caught exception: " + e);
    }
}

risky();
