-- Universal Key Authentication System (accepts any key)
local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local LocalPlayer = Players.LocalPlayer

-- Check if key is valid (now accepts any non-empty key)
local function IsValidKey(inputKey)
    -- Accept any key that isn't empty or just whitespace
    return inputKey and string.len(string.gsub(inputKey, "%s", "")) > 0
end

-- Create authentication GUI
local function CreateAuthGUI()
    local ScreenGui = Instance.new("ScreenGui")
    ScreenGui.Name = "KeyAuthSystem"
    ScreenGui.Parent = LocalPlayer:WaitForChild("PlayerGui")

    -- Main Frame
    local MainFrame = Instance.new("Frame")
    MainFrame.Name = "AuthFrame"
    MainFrame.Size = UDim2.new(0, 300, 0, 200)
    MainFrame.Position = UDim2.new(0.5, -150, 0.5, -100)
    MainFrame.BackgroundColor3 = Color3.fromRGB(30, 30, 40)
    MainFrame.BorderSizePixel = 2
    MainFrame.BorderColor3 = Color3.fromRGB(100, 100, 150)
    MainFrame.Parent = ScreenGui

    -- Title
    local Title = Instance.new("TextLabel")
    Title.Name = "Title"
    Title.Size = UDim2.new(1, 0, 0, 40)
    Title.BackgroundColor3 = Color3.fromRGB(50, 50, 70)
    Title.BorderSizePixel = 0
    Title.Text = "Key Authentication"
    Title.TextColor3 = Color3.fromRGB(255, 255, 255)
    Title.TextSize = 18
    Title.Font = Enum.Font.GothamBold
    Title.Parent = MainFrame

    -- Instructions
    local Instructions = Instance.new("TextLabel")
    Instructions.Name = "Instructions"
    Instructions.Size = UDim2.new(0.9, 0, 0, 30)
    Instructions.Position = UDim2.new(0.05, 0, 0.25, 0)
    Instructions.BackgroundTransparency = 1
    Instructions.Text = "Enter any key to continue:"
    Instructions.TextColor3 = Color3.fromRGB(200, 200, 200)
    Instructions.TextSize = 14
    Instructions.Font = Enum.Font.Gotham
    Instructions.Parent = MainFrame

    -- Key Input Box
    local KeyInput = Instance.new("TextBox")
    KeyInput.Name = "KeyInput"
    KeyInput.Size = UDim2.new(0.8, 0, 0, 35)
    KeyInput.Position = UDim2.new(0.1, 0, 0.45, 0)
    KeyInput.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
    KeyInput.BorderSizePixel = 1
    KeyInput.BorderColor3 = Color3.fromRGB(80, 80, 100)
    KeyInput.Text = ""
    KeyInput.PlaceholderText = "Enter any key here..."
    KeyInput.TextColor3 = Color3.fromRGB(255, 255, 255)
    KeyInput.PlaceholderColor3 = Color3.fromRGB(150, 150, 150)
    KeyInput.TextSize = 14
    KeyInput.Font = Enum.Font.Gotham
    KeyInput.Parent = MainFrame

    -- Submit Button
    local SubmitButton = Instance.new("TextButton")
    SubmitButton.Name = "SubmitButton"
    SubmitButton.Size = UDim2.new(0.35, 0, 0, 30)
    SubmitButton.Position = UDim2.new(0.1, 0, 0.7, 0)
    SubmitButton.BackgroundColor3 = Color3.fromRGB(70, 130, 70)
    SubmitButton.BorderSizePixel = 1
    SubmitButton.BorderColor3 = Color3.fromRGB(50, 100, 50)
    SubmitButton.Text = "Submit"
    SubmitButton.TextColor3 = Color3.fromRGB(255, 255, 255)
    SubmitButton.TextSize = 14
    SubmitButton.Font = Enum.Font.GothamBold
    SubmitButton.Parent = MainFrame

    -- Cancel Button
    local CancelButton = Instance.new("TextButton")
    CancelButton.Name = "CancelButton"
    CancelButton.Size = UDim2.new(0.35, 0, 0, 30)
    CancelButton.Position = UDim2.new(0.55, 0, 0.7, 0)
    CancelButton.BackgroundColor3 = Color3.fromRGB(130, 70, 70)
    CancelButton.BorderSizePixel = 1
    CancelButton.BorderColor3 = Color3.fromRGB(100, 50, 50)
    CancelButton.Text = "Cancel"
    CancelButton.TextColor3 = Color3.fromRGB(255, 255, 255)
    CancelButton.TextSize = 14
    CancelButton.Font = Enum.Font.GothamBold
    CancelButton.Parent = MainFrame

    -- Status Label
    local StatusLabel = Instance.new("TextLabel")
    StatusLabel.Name = "StatusLabel"
    StatusLabel.Size = UDim2.new(0.9, 0, 0, 20)
    StatusLabel.Position = UDim2.new(0.05, 0, 0.85, 0)
    StatusLabel.BackgroundTransparency = 1
    StatusLabel.Text = ""
    StatusLabel.TextColor3 = Color3.fromRGB(255, 100, 100)
    StatusLabel.TextSize = 12
    StatusLabel.Font = Enum.Font.Gotham
    StatusLabel.Parent = MainFrame

    -- Event Handlers
    SubmitButton.MouseButton1Click:Connect(function()
        local inputKey = KeyInput.Text
        
        if inputKey == "" or string.len(string.gsub(inputKey, "%s", "")) == 0 then
            StatusLabel.Text = "Please enter a key"
            StatusLabel.TextColor3 = Color3.fromRGB(255, 100, 100)
            return
        end
        
        if IsValidKey(inputKey) then
            StatusLabel.Text = "Key accepted! Access granted."
            StatusLabel.TextColor3 = Color3.fromRGB(100, 255, 100)
            
            -- Wait a moment then close auth GUI
            game:GetService("Debris"):AddItem(ScreenGui, 2)
            
            -- Here you would launch your main application
            OnAuthenticationSuccess()
            
        else
            -- This should never happen now, but keeping for safety
            StatusLabel.Text = "Invalid key. Access denied."
            StatusLabel.TextColor3 = Color3.fromRGB(255, 100, 100)
            KeyInput.Text = ""
        end
    end)
    
    CancelButton.MouseButton1Click:Connect(function()
        ScreenGui:Destroy()
    end)
    
    -- Enter key support
    KeyInput.FocusLost:Connect(function(enterPressed)
        if enterPressed then
            SubmitButton.MouseButton1Click:Fire()
        end
    end)
end

-- Function called when authentication succeeds
function OnAuthenticationSuccess()
    print("Authentication successful!")
    
    -- Create a simple success message
    local SuccessGui = Instance.new("ScreenGui")
    SuccessGui.Name = "SuccessMessage"
    SuccessGui.Parent = LocalPlayer:WaitForChild("PlayerGui")
    
    local SuccessFrame = Instance.new("Frame")
    SuccessFrame.Size = UDim2.new(0, 250, 0, 100)
    SuccessFrame.Position = UDim2.new(0.5, -125, 0.5, -50)
    SuccessFrame.BackgroundColor3 = Color3.fromRGB(50, 100, 50)
    SuccessFrame.BorderSizePixel = 2
    SuccessFrame.BorderColor3 = Color3.fromRGB(100, 150, 100)
    SuccessFrame.Parent = SuccessGui
    
    local SuccessLabel = Instance.new("TextLabel")
    SuccessLabel.Size = UDim2.new(1, 0, 1, 0)
    SuccessLabel.BackgroundTransparency = 1
    SuccessLabel.Text = "Access Granted!\nWelcome, " .. LocalPlayer.Name
    SuccessLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
    SuccessLabel.TextSize = 16
    SuccessLabel.Font = Enum.Font.GothamBold
    SuccessLabel.Parent = SuccessFrame
    
    -- Auto-close after 3 seconds
    game:GetService("Debris"):AddItem(SuccessGui, 3)
    
    -- Here you would start your main application
end

-- Start the authentication process
CreateAuthGUI()