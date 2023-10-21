#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(arrow)
library(tidyverse)
results <- read_csv('https://raw.githubusercontent.com/ohiopolitics/voters/Shiny%20Apps/Example%20Model%20Outputs.csv') %>%
  mutate(likely_score = abs(50-Chance_Vote))

# Define UI for application that draws a histogram
ui <- fluidPage(
  titlePanel("Register People to Vote"),
  sidebarLayout(
    sidebarPanel(
      checkboxGroupInput("precinct", "Select Precinct:", 
                         choices = unique(results$Precinct),
                         selected = unique(results$Precinct)),
      selectInput("age_category", "Select Age Category:", choices = c("All", "Under 18", "18-35", "36-50", "Over 50")),
      numericInput("num_results", "Number of Results:", value = 10, min = 1),
      downloadButton("download_csv", "Download Filtered Results")
    ),
    mainPanel(
      tableOutput("filtered_results")
    )
  )
)




# Define server logic required to draw a histogram
server <- function(input, output) 
  {
    # Create a reactive expression for filtered results
    filtered_data <- reactive({
      # Filter the results dataframe based on user inputs
      filtered <- results
      
      if (input$age_category != "All") {
        age_ranges <- list(
          "Under 18" = c(0, 18),
          "18-35" = c(19, 35),
          "36-50" = c(36, 50),
          "Over 50" = c(51, max(results$Age))
        )
        age_range <- age_ranges[[input$age_category]]
        filtered <- filtered[filtered$Age >= age_range[1] & filtered$Age <= age_range[2], ]
      }
      
      filtered <- filtered %>%
        filter(Precinct %in% input$precinct) %>%
        arrange(likely_score) %>%
        select(-c(likely_score,Vote_Dem)) %>%
        head(n=ifelse(input$num_results>length(filtered),input$num_results,length(filtered)))
    })
    
    # Render the table of filtered results
    output$filtered_results <- renderTable({
      filtered_data()
    })
    
    # Define a download handler for the CSV file
    output$download_csv <- downloadHandler(
      filename = function() {
        paste("filtered_results_", Sys.Date(), ".csv", sep = "")
      },
      content = function(file) {
        write.csv(filtered_data(), file, row.names = FALSE)
      }
    )
  }


# Run the application 
shinyApp(ui = ui, server = server)
  