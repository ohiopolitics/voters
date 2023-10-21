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
results <- read_csv('https://raw.githubusercontent.com/ohiopolitics/voters/main/Spencer%20Misc/Adams.csv')
counties <- read_csv('https://raw.githubusercontent.com/ohiopolitics/voters/main/Spencer%20Misc/County%20Codes.csv') %>%
  mutate(County=str_replace(County,' County',''))

# Define UI for application that draws a histogram
ui <- fluidPage(
  titlePanel("Get Donations"),
  sidebarLayout(
    sidebarPanel(
      radioButtons('demrep',"Select your Affiliation:",
                   choices = c("Democrat","Republican"),
                   selected = 'Democrat'),
      selectInput("county", "Select County:", 
                  choices = unique(counties$County),
                  selected = "Adams"),
      selectInput("age_category", "Select Age Category:", c("All", "18-24", "25-34","35-44","45-54","55-64","65+")),
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
    filtered <- read_csv(paste0('https://raw.githubusercontent.com/ohiopolitics/voters/main/Spencer%20Misc/',input$county,".csv"))
    
    if (input$age_category != "All") {
      age_ranges <- list(
        "18-24" = c(18, 24),
        "25-34" = c(25, 34),
        "35-44" = c(35, 44),
        "45-54" = c(45,54),
        "55-64" = c(55,64),
        "65+" = c(65, max(filtered$Age))
      )
      age_range <- age_ranges[[input$age_category]]
      filtered <- filter(filtered, Age >= age_range[1] & Age <= age_range[2])
    }

      
    filtered <- filtered %>%
      filter(County %in% input$county)
    
    if(input$demrep == 'Republican') {
      filtered <- filtered %>%
        arrange(desc(R_probs-D_probs)) %>%
        select(-c(D_probs,VT_prediction))
        
    }
    if(input$demrep == 'Democrat') {
      filtered <- filtered %>%
        arrange(desc(D_probs-R_probs)) %>%
        select(-c(R_probs,VT_prediction)) #%>%
        #head(n=ifelse(input$num_results>=length(filtered$County),input$num_results,length(filtered$County)))
    }
    filtered <- head(filtered, n=ifelse(input$num_results<length(filtered$County),input$num_results,length(filtered$County)))
  })
  
  # Render the table of filtered results
  output$filtered_results <- renderDT({
    filtered_data()},options=list(dom = 't'))
  
  # Define a download handler for the CSV file
  output$download_csv <- downloadHandler(
    filename = function() {
      paste("persuaded_voters_", Sys.Date(), ".csv", sep = "")
    },
    content = function(file) {
      write.csv(filtered_data() %>%
                  mutate(User_Respose=''), file, row.names = FALSE)
    }
  )
}


# Run the application 
shinyApp(ui = ui, server = server)
