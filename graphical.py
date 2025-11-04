from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def solve_lp(constraints, objective):
    def intersect(line1, line2):
        a1, b1, c1 = line1
        a2, b2, c2 = line2
        D = a1 * b2 - a2 * b1
        if abs(D) < 1e-12:
            return None
        x = (c1 * b2 - c2 * b1) / D
        y = (a1 * c2 - a2 * c1) / D
        return (x, y)

    p, q = objective
    points = []

    # пересечения пар линий
    for i in range(len(constraints)):
        for j in range(i + 1, len(constraints)):
            pt = intersect(constraints[i], constraints[j])
            if pt is not None:
                points.append(pt)

    # пересечения с осями
    for (a, b, c) in constraints:
        if abs(b) > 1e-12:
            y = c / b
            if y >= 0:
                points.append((0, y))
        if abs(a) > 1e-12:
            x = c / a
            if x >= 0:
                points.append((x, 0))

    # проверка точек на допустимость
    valid_points = []
    for (x, y) in points:
        if x < -1e-9 or y < -1e-9:
            continue
        ok = True
        for (a, b, c) in constraints:
            if a * x + b * y > c + 1e-9:
                ok = False
                break
        if ok:
            valid_points.append((x, y))

    # удалим почти-совпадающие точки
    uniq = []
    for pnt in valid_points:
        if not any(abs(u[0]-pnt[0])<1e-7 and abs(u[1]-pnt[1])<1e-7 for u in uniq):
            uniq.append(pnt)
    valid_points = uniq

    if len(valid_points) == 0:
        return {
            "status": "infeasible",
            "valid_points": [],
            "best_point": None,
            "best_value": None
        }

    # посчитаем min и max значений целевой
    best_min_val = None
    best_min_pt = None
    best_max_val = None
    best_max_pt = None
    for (x, y) in valid_points:
        Z = p * x + q * y
        if best_min_val is None or Z < best_min_val:
            best_min_val = Z
            best_min_pt = (x, y)
        if best_max_val is None or Z > best_max_val:
            best_max_val = Z
            best_max_pt = (x, y)

    return {
        "status": "optimal",
        "valid_points": valid_points,
        "best_min_point": best_min_pt,
        "best_min_value": best_min_val,
        "best_max_point": best_max_pt,
        "best_max_value": best_max_val
    }

@app.route('/solve', methods=['POST'])
def solve_route():
    """
    Ожидает JSON:
    {
      "constraints": [[a,b,c], ...],
      "objective": [p,q],
      "type": "min" | "max"   # необязательное, для удобства UI
    }
    Возвращает JSON с результатом (см. solve_lp).
    """
    data = request.get_json(force=True)
    constraints = data.get('constraints', [])
    objective = data.get('objective', [0,0])
    sol = solve_lp(constraints, objective)
    # если клиент попросил конкретный type, можно вернуть только нужный best_point/value
    typ = data.get('type')
    if typ == 'min' and sol['status']=='optimal':
        sol['best_point'] = sol['best_min_point']
        sol['best_value'] = sol['best_min_value']
    elif typ == 'max' and sol['status']=='optimal':
        sol['best_point'] = sol['best_max_point']
        sol['best_value'] = sol['best_max_value']
    return jsonify(sol)

if __name__ == '__main__':
    # pip install flask flask-cors
    app.run(host='0.0.0.0', port=5000, debug=True)