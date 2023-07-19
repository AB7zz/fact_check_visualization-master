const timeline = document.getElementById('timeline');

const svg = d3.select("body").append("svg")
    .attr("width", 5000)
    .attr("height", 5000)
    .attr('id', 'outside')
const outside = document.getElementById('outside')

const json = JSON.parse(localStorage.getItem('json'))
function generate(){
    var edges = [];
    const sortedNodes = json.nodes.sort((a, b) => b.year[0] - a.year[0])
    console.log('lol', sortedNodes)
    json.links.forEach(function(e, i) {
        var sourceNode = sortedNodes.filter(function(n) {
            return n.id === e.source;
        })[0],
            targetNode = sortedNodes.filter(function(n) {
                return n.id === e.target;
            })[0];
    
        edges.push({
            source: sourceNode,
            target: targetNode,
            value: e.value
        });
    });


    d3.forceSimulation(sortedNodes)                 
        .force("link", d3.forceLink(edges))
    
    const arrows = svg
        .selectAll('defs')
        .data(edges)
        .enter()
        .append("svg:defs")
        .append("svg:marker")
        .attr('id', 'arrow')
        .attr('refX', -108)
        .attr('refY', 0)
        .attr("viewBox", "0 -5 10 10")
        .attr("markerWidth", 20)
        .attr("markerHeight", 10)
        .attr("orient", "auto")
        
    
    arrows
        .append("svg:path")
        .attr("d", "M0,-5L10,0L0,5");


    const link = svg
        .selectAll("line")
        .data(edges)
        .enter()
        .append("line")
        .attr('class', 'lines')
        .style( "stroke", "#000" )
        .attr('marker-start', (d) => `url(#arrow)`)
        .style( "stroke-width", 1.5 );

    const node = svg
        .selectAll('foreignObject')
        .data(sortedNodes)
        .enter()
        .append('foreignObject')
        .attr('id', data => `${data.id}`)
        .attr('height', '100%')
        .attr('width', 350)

    function bottomYear(x, y, year){
        svg
            .append('text')
            .text(year)
            .attr('fill', 'red')
            .attr('font-size', '25px')
            .attr('font-weight', 'bold')
            .attr('x', x+150)
            .attr('y', y+500)
    }
    function newBottomYear(x, y, year){
        svg
            .append('text')
            .text(year)
            .attr('fill', 'red')
            .attr('font-size', '25px')
            .attr('font-weight', 'bold')
            .attr('x', x+150)
            .attr('y', y+500)
    }
    function topYear(x, year){
        svg
            .append('text')
            .text(year)
            .attr('fill', 'red')
            .attr('font-size', '25px')
            .attr('font-weight', 'bold')
            .attr('x', x+150)
            .attr('y', 100)
    }
    
    const yAxis = []
    const xAxis = []
    const timelineset = []
    let maxyear = 2023
    let minyear = 2010
    
    node 
        .attr('class', (d) => `l${d.id} nodes`)
        .html( function(data){
            if(data.type == "evidence"){
                return '<div class="box"><p class="boxfirstline fit-text">' + data.snippet + '</p><a target="_blank" style="text-decoration: none" href="' + data.source + '" class="boxsecondline fit-text">'+data.source+'</a><hr class="solid"><p class="boxdate">' + data.year + '</p></div>';
            }else if(data.type == "claim" && data.id!=0){
                return '<div class="claimbox tri-right2 btm-left-in2 border2 sb32"><p class="claimfirstline fit-text">' + data.snippet + '</p><p class="claimsecondline fit-text">'+data.claimer +'</p><hr class="solid"><p class="claimdate">' + data.year + '</p></div>';
            }else if(data.type == "claim" && data.id==0){
                return '<div class="greenclaim tri-right btm-left-in border sb32"><p class="greenclaimfirstline fit-text">' + data.snippet + '</p><p class="greenclaimsecondline fit-text">'+data.claimer +'</p><hr class="solid"><p class="claimdate">' + data.year + '</p></div>';
            }
            else if(data.type == "fact_check"){
                return '<div class="fact_check"><p class="fact_checkfirstline fit-text">' + data.snippet + '</p><a target="_blank" href="' + data.source + '"  class="fact_checksecondline fit-text">'+data.source +'</a><p class="fact_checkthirdline">Truth value: '+data.truth_value +'</p><hr class="solid"><p class="fact_checkdate">' + data.year + '</p></div>';
            }
        })
        // .call(d3.drag()
        //         .on('start', dragstarted)
        //         .on('drag', dragged)
        //         .on('end', dragended)
        // )
        .attr("x", function(d){
            let xi
            let year = d.year[0]
            // if(year == 0 || d.year == "UNKNOWN"){
            //     year = maxyear
            //     xi = ((maxyear-year)*400)+20
            // }else{
            //     xi = ((maxyear-year)*400)+20
            // }
            if(year == 0 || year == "UNKNOWN"){
                year = sortedNodes[0].year[0]
                // xi = 20
            }

            if(xAxis.length == 0){
                xi = 20
            }else if(!xAxis[maxyear - year]){
                xi = xAxis[xAxis.length - 1] + 400
            }else if(xAxis[maxyear - year]){
                xi = xAxis[maxyear-year]
            }
            xAxis[maxyear - year] = xi
            d.x = parseFloat(xi)
            console.log(xAxis)
            return xi;
        })
        .attr("y", function(d){
            let i, yi
            i = 0
            let year = d.year[0]
            while(sortedNodes[i].id!=d.id){
                i++
            }

            if(year == "UNKNOWN"){
                year = sortedNodes[0].year[0]
            }

            if(!yAxis[maxyear-year]){
                yAxis[maxyear-year] = 200
            }
            else{
                yAxis[maxyear-year] += 500
            }
            yi = yAxis[maxyear-year]
            d.y = parseFloat(yi)
            return yi;  
        })
        .attr('timeline', (d) => {
            let ymax=sortedNodes[0].y, xmax=sortedNodes[0].x
            let year = d.year[0]
            if(year == "UNKNOWN"){
                year = sortedNodes[0].year[0]
            }
            for(let l = 1; l < sortedNodes.length; l++){
                if(sortedNodes[l].y >= ymax){
                    ymax = sortedNodes[l].y
                }
                if(sortedNodes[l].x >= xmax){
                    xmax = sortedNodes[l].x
                }
            }
            if(!timelineset[year]){
                bottomYear(d.x, ymax, year)
                topYear(d.x, year)
                timelineset[year] = true
            }
            svg
                .attr("height", ymax+1000)
                .attr("width", xmax+1000)
        })
    
    

    link
        .attr("x1", function(d){
            x1 = d.source.x + 150;
            return x1
        })
        .attr("y1", function(d){
            y1 = d.source.y+75;
            return y1
        })
        .attr("x2", function(d){
            x2 = d.target.x+150;
            return x2
        })
        .attr("y2", function(d){
            y2 = d.target.y+75;
            return y2
        })
        .attr( "d", function(d){
            x1 = d.source.x + 150;
            y1 = d.source.y+75;
            x2 = d.target.x+150;
            y2 = d.target.y+75;
            return "M" + x1 + "," + y1 + ", " + x2 + "," + y2
        })
    link.each(function(d){
        let source = d.source.id
        let target = d.target.id
        this.classList.add(`l${source}`)
        this.classList.add(`l${target}`)

        let snodesource = document.getElementById(`${source}`)
        let snodetarget = document.getElementById(`${target}`)
        snodetarget.classList.add(`l${source}`)
        snodesource.classList.add(`l${target}`)
    })

    svg
        .on('click', (evt) => {
            let target = evt.target
            let lines = document.getElementsByClassName('lines')
            let allnodes = document.getElementsByClassName('nodes')
            if(outside == target){
                for(let i=0; i<lines.length; i++){
                    lines[i].style.opacity = '1'
                    lines[i].style.stroke = 'black'
                    lines[i].style.strokeWidth = '1.5'
                }
    
                for(let i=0; i<allnodes.length; i++){
                    allnodes[i].style.opacity = '1'
                    allnodes[i].style.pointerEvents = 'all'
                }
                return
            }
        }
    )

    node
        .on('click', function(){
            let lines = document.getElementsByClassName('lines')
            let allnodes = document.getElementsByClassName('nodes')
            for(let i=0; i<lines.length; i++){
                if(!lines[i].classList.contains(`l${this.id}`)){
                    lines[i].style.opacity = '0.03'
                }else{
                    lines[i].style.stroke = 'red'
                }
            }

            for(let i=0; i<allnodes.length; i++){
                if(!allnodes[i].classList.contains(`l${this.id}`)){
                    allnodes[i].style.opacity = '0.15'
                    allnodes[i].style.pointerEvents = 'none'
                }
            }
        })
    
    



    
    // function dragstarted(event, d) {
    //     d3.select(this)
    //         .attr("fx", d.x = event.x )
    //         .attr("fy", d.y = event.y )
        
    //     ticked()
    // }

    // function dragged(event, d) { 
    //     d3.select(this)
    //         .attr("fx", d.x = event.x )
    //         .attr("fy", d.y = event.y )
        
    //     ticked()
    // }

    // function dragended(event, d) {
    //     d3.select(this)
    //         .attr("fx", d.x = event.x )
    //         .attr("fy", d.y = event.y )
    //         .attr('lol', id = d.id, x=d.x, y=d.y, vx=d.vx, vy=d.vy )
        
    //     ticked()

    // }

    // function ticked() {
    //     link
    //         .attr("x1", d => d.source.x+150)
    //         .attr("x2", d => d.target.x+150)
    //         .attr("y1", d => d.source.y+75)
    //         .attr("y2", d => d.target.y+75)

    //     node
    //         .attr("x", d => d.x )   
    //         .attr("y", d => d.y )
    // }
// })
}

generate()