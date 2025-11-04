def solve_lp(constraints, objective):
    def intersect(line1, line2):
        # line: a*x + b*y = c
        a1, b1, c1 = line1
        a2, b2, c2 = line2

        D = a1 * b2 - a2 * b1  # детерминант

        if D == 0:
            return None

        x = (c1 * b2 - c2 * b1) / D
        y = (a1 * c2 - a2 * c1) / D

        return (x, y)

    p, q = objective 

    points = []

    for i in range(len(constraints)):
        for j in range(i + 1, len(constraints)):
            pt = intersect(constraints[i], constraints[j])
            if pt is not None:
                points.append(pt)

    for (a, b, c) in constraints:
        # x = 0 -> b*y = c
        if b != 0:
            y = c / b
            if y >= 0:
                points.append((0, y))

        # y = 0 -> a*x = c
        if a != 0:
            x = c / a
            if x >= 0:
                points.append((x, 0))


    valid_points = []
    for (x, y) in points:
        if x < 0 or y < 0:
            continue

        ok = True
        for (a, b, c) in constraints:
            if a * x + b * y > c + 1e-9:
                ok = False
                break

        if ok:
            valid_points.append((x, y))

    best_val = None
    best_pt = None

    for (x, y) in valid_points:
        Z = p * x + q * y
        if best_val is None or Z < best_val:
            best_val = Z
            best_pt = (x, y)

    return {
        "best_point": best_pt,
        "max_value": best_val,
        "valid_points": valid_points
    }



constraints = [
    (1000, 2400, 12000),  
    (-650, -500, -1600),   
    (650, 500, 3200),   
    (-500, 1300, 0),   
]

objective = (1000, 2400)  

result = solve_lp(constraints, objective)
print(result)
