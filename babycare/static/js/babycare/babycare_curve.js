document.addEventListener('DOMContentLoaded', function () {
    function showGuidelines(circleElement, data, guidelineGroup, unitName) {
        const circle = d3.select(circleElement);
        const cx = circle.attr("cx");
        const cy = circle.attr("cy");
        
        // 获取坐标轴位置
        const xAxisY = marginLeft;
        const yAxisX = height - marginBottom;
        
        // 创建到 x 轴的虚线（垂直线）
        guidelineGroup.append("line")
            .attr("class", "guideline x-guideline")
            .attr("x1", cx)
            .attr("y1", cy)
            .attr("x2", cx)
            .attr("y2", yAxisX)
            .attr("stroke", "#999")
            .attr("stroke-dasharray", "7,5,2,5")
            .attr("stroke-width", 1);
        
        // 创建到 y 轴的虚线（水平线）
        guidelineGroup.append("line")
            .attr("class", "guideline y-guideline")
            .attr("x1", cx)
            .attr("y1", cy)
            .attr("x2", xAxisY)
            .attr("y2", cy)
            .attr("stroke", "#999")
            .attr("stroke-dasharray", "7,5,2,5")
            .attr("stroke-width", 1);

        const dateString = d3.timeFormat("%y/%m/%d")(new Date(data.datetime));
        const guidelineText1 = `${dateString}`;
        const guidelineText2 = `${data.yData} ${unitName}`;
        guidelineGroup.append("text")
            .attr("class", "guideline guideline-text")
            .attr("x", cx)
            .attr("y", cy - 10)
            .attr("text-anchor", "middle")
            .attr("font-size", "1em")
            .attr("fill", "rebeccapurple")
            .text(guidelineText2);
        guidelineGroup.append("text")
            .attr("class", "guideline guideline-text")
            .attr("x", cx)
            .attr("y", cy - 26)
            .attr("text-anchor", "middle")
            .attr("font-size", "1em")
            .attr("fill", "rebeccapurple")
            .text(guidelineText1);
    }
    function hideGuidelines(guidelineGroup) {
        guidelineGroup.selectAll(".guideline").remove();
    }

    function getWeek(datetime, startDate) {
        const diffInMilliseconds = datetime - startDate;
        const diffInDays = diffInMilliseconds / (1000 * 60 * 60 * 24);
        const weeks = diffInDays / 7;
        return weeks;
    }

    // Declare the chart dimensions and margins.
    const width = Math.min(document.body.clientWidth - 24, 640);  // 主容器左右各有12的padding
    const height = 300;
    const marginTop = 60;
    const marginRight = 30;
    const marginBottom = 30;
    const marginLeft = 30;
    document.querySelectorAll(".fenton-curve").forEach(function (element) {
        const startDate = new Date(element.dataset.startDate);
        const fentonCurveUrl = element.dataset.fentonCurveUrl;
        const curveDataUrl = element.dataset.curveDataUrl;
        const fentonType = element.dataset.fentonType;
        const unitName = fentonType === "weight" ? "kg" : "cm"

        if (fentonCurveUrl === "") {
            element.textContent = "填入宝宝性别后才能查看曲线";
            return;
        }

        fetch(curveDataUrl)
            .then(response => response.json())
            .then(growthData => {
                if (growthData.length === 0) {
                    element.textContent = "尚未记录宝宝相关数据";
                    return;
                }
                const dataWeeks = growthData.map(item => getWeek(new Date(item.datetime), startDate));
                let minWeek = Math.min(...dataWeeks);
                minWeek = Math.floor(Math.max(minWeek - 1, 22));
                let maxWeek = Math.max(...dataWeeks);
                maxWeek = Math.ceil(Math.min(maxWeek + 1, 50));
                const dataValues = growthData.map(item => item.yData);
                let maxValue = Math.max(...dataValues);
                maxValue = Math.ceil(maxValue);
                let minValue = Math.min(...dataValues);
                minValue = Math.floor(minValue);

                fetch(fentonCurveUrl)
                    .then(response => response.json())
                    .then(fentonCurveData => {
                        const filteredFentonCurveData = d3.filter(
                            fentonCurveData, 
                            d => (d.week >= minWeek && d.week <= maxWeek && 
                                (d.type === "3%" || d.type === "10%" || d.type === "50%" || d.type === "90%" || d.type === "97%"))
                        );

                        const fentonMinValue = Math.floor(Math.min(...filteredFentonCurveData.map(d => d.yData)));
                        minValue = Math.min(minValue, fentonMinValue);
                        const fentonMaxValue = Math.ceil(Math.max(...filteredFentonCurveData.map(d => d.yData)));
                        maxValue = Math.max(maxValue, fentonMaxValue);

                        // Declare the x (horizontal position) scale.
                        const x = d3.scaleLinear()
                            .domain([minWeek, maxWeek])
                            .range([marginLeft, width - marginRight]);
                        const xTicks = Math.floor(width / 64);

                        // Declare the y (vertical position) scale.
                        const y = d3.scaleLinear()
                            .domain([minValue, maxValue])
                            .range([height - marginBottom, marginTop]);

                        // Create the SVG container.
                        const svg = d3.create("svg")
                            .attr("width", width)
                            .attr("height", height)
                            .attr("style", "fill:grey;");

                        // Add the x-axis.
                        svg.append("g")
                            .attr("transform", `translate(0,${height - marginBottom})`)
                            .call(d3.axisBottom(x).ticks(xTicks))
                            .selectAll("text")
                            .style("font-size", "1.5em");

                        // Add the y-axis.
                        svg.append("g")
                            .attr("transform", `translate(${marginLeft},0)`)
                            .call(d3.axisLeft(y))
                            .selectAll("text")
                            .style("font-size", "1.5em");

                        const line = d3.line()
                            .x((d) => x(d.week))
                            .y((d) => y(d.yData))
                            .curve(d3.curveCardinal.tension(1));

                        const groupedData = d3.group(filteredFentonCurveData, d => d.type);

                        const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

                        groupedData.forEach((groupData, groupName) => {
                            // 对每组数据按b属性排序以确保曲线正确连接
                            const sortedData = Array.from(groupData).sort((a, b) => a.week - b.week);

                            const g = svg.append("g");
                            
                            g.append("path")
                                .datum(sortedData)
                                .attr("fill", "none")
                                .attr("stroke", colorScale(groupName))
                                .attr("stroke-width", 0.5)
                                .attr("d", line);
                        });

                        
                        // 生长数据点
                        const growthDataGroup = svg.append("g");
                        growthDataGroup.selectAll("circle")
                        .data(growthData)
                        .enter()
                        .append("circle")
                        .attr("cx", (d) => x(getWeek(new Date(d.datetime), startDate)))
                        .attr("cy", (d) => y(d.yData))
                        .attr("r", 3)
                        .attr("fill", "blue")
                        .on("mouseover", function(event, d) {
                            showGuidelines(this, d, guidelineGroup, unitName);
                        })
                        .on("mouseout", function() {
                            hideGuidelines(guidelineGroup);
                        });
                        
                        const guidelineGroup = svg.append("g").attr("class", "guidelines");

                        element.append(svg.node());
                    }
                );
            }
        );
    });
});