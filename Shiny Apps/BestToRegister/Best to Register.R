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
library(DT)
results <- read_csv('https://raw.githubusercontent.com/ohiopolitics/voters/main/Spencer%20Misc/Adams.csv') %>%
  mutate(likely_score = 1-abs(.5-VT_prediction))
counties <- read_csv('https://raw.githubusercontent.com/ohiopolitics/voters/main/Spencer%20Misc/County%20Codes.csv') %>%
  mutate(County=str_replace(County,' County',''))

# Define UI for application that draws a histogram
ui <- fluidPage(
  titlePanel("Register People to Vote"),
  sidebarLayout(
    sidebarPanel(
      selectInput("county", "Select County:", 
                         choices = unique(counties$County),
                         selected = "Adams"),
      selectInput("age_category", "Select Age Category:", choices = c("All", "Under 18", "18-35", "36-60", "Over 60")),
      numericInput("num_results", "Number of Results:", value = 10, min = 1),
      downloadButton("download_csv", "Download Filtered Results")
    ),
    mainPanel(
      DTOutput("filtered_results")
    )
  )
)




# Define server logic required to draw a histogram
server <- function(input, output) 
  {
    # Create a reactive expression for filtered results
    filtered_data <- reactive({
      # Filter the results dataframe based on user inputs
      filtered <- read_csv(paste0('https://raw.githubusercontent.com/ohiopolitics/voters/main/Spencer%20Misc/',input$county,".csv")) %>%
        mutate(likely_score = 1-abs(.5-VT_prediction))
      
      if (input$age_category != "All") {
        age_ranges <- list(
          "Under 18" = c(0, 18),
          "18-35" = c(19, 35),
          "36-60" = c(36, 60),
          "Over 60" = c(61, max(filtered$Age))
        )
        age_range <- age_ranges[[input$age_category]]
        filtered <- filter(filtered, Age >= age_range[1] & Age <= age_range[2])
      }
      
      filtered <- filtered %>%
        filter(County %in% input$county) %>%
        arrange(desc(likely_score)) %>%
        select(last_name,first_name,street_address,Age,County,likely_score) %>% #Add back other column
        head(n=ifelse(input$num_results>length(filtered$county),input$num_results,length(filtered)))
    })
    
    # Render the table of filtered results
    output$filtered_results <- renderDT({
      filtered_data()}
    )
    
    # Define a download handler for the CSV file
    output$download_csv <- downloadHandler(
      filename = function() {
        paste("potential_voters_", Sys.Date(), ".csv", sep = "")
      },
      content = function(file) {
        write.csv(filtered_data() %>%
                    mutate(User_Respose=''), file, row.names = FALSE)
      }
    )
  }


# Run the application 
shinyApp(ui = ui, server = server)
  