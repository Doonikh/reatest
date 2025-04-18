document.addEventListener('DOMContentLoaded', function() {
    // Находим все строки в таблице результатов админки.
    var rows = document.querySelectorAll('tr.result');
    // Если строки не имеют класса "result", выбираем все строки внутри <tbody>
    if (rows.length === 0) {
        rows = document.querySelectorAll('tbody tr');
    }

    rows.forEach(function(row) {
        var statusCell = row.querySelector('td.field-status');
        if (statusCell) {
            // Получаем статус из выпадающего списка или из текста ячейки
            var selectElem = statusCell.querySelector('select');
            var statusText = selectElem ? selectElem.value : statusCell.textContent.trim();
            statusText = statusText.toLowerCase();

            // Устанавливаем цвет фона строки в зависимости от статуса
            if (statusText === 'new' || statusText === 'новая') {
                row.style.backgroundColor = '#ffe0e0'; // светло-красный
            } else if (statusText === 'in_progress' || statusText === 'в работе') {
                row.style.backgroundColor = '#faffc3'; // светло-оранжевый
            } else if (statusText === 'closed' || statusText === 'закрыта') {
                row.style.backgroundColor = '#e0ffe0'; // светло-зеленый
            } else if (statusText === 'denied' || statusText === 'отклонена') {
                row.style.backgroundColor = '#a7d7ff'; // светло-голубой
            }

            // Устанавливаем цвет текста внутри строки на черный
            row.style.color = 'black';

            // Для всех ячеек внутри строки устанавливаем вертикальное центрирование
            // Если нужно горизонтальное центрирование, добавьте text-align: center;
            var cells = row.querySelectorAll('td, th');
            cells.forEach(function(cell) {
                cell.style.verticalAlign = 'middle';
                cell.style.textAlign = 'center'; // если требуется горизонтальное центрирование
            });
        }
    });
});
